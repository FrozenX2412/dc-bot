import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Optional, List

class Whois(commands.Cog):
    """Show detailed user information in an embed. Hybrid command (prefix + slash)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="whois",
        aliases=["userinfo", "ui"],
        description="Show information about a user (or yourself)."
    )
    @app_commands.describe(user="The member to look up (defaults to yourself).")
    async def whois(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """
        Works as both a prefix command and a slash command.
        Examples:
          - /whois user:@someone
          - !whois
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        try:
            subject: discord.User | discord.Member
            if is_interaction:
                subject = user or ctx.user
                requestor = ctx.user
            else:
                subject = user or ctx.author
                requestor = ctx.author

            # If a Member was provided (guild context) use that; otherwise try to fetch member from guild
            member: Optional[discord.Member] = None
            if isinstance(subject, discord.Member):
                member = subject
            else:
                # Not a member object: if command used in a guild, try to resolve
                if getattr(ctx, "guild", None):
                    member = ctx.guild.get_member(subject.id) or None

            # Basic info
            title = f"Whois — {subject}"
            embed = discord.Embed(title=title, color=discord.Color.green(), timestamp=discord.utils.utcnow())

            # Avatar
            avatar_url = getattr(subject, "display_avatar", None)
            if avatar_url:
                embed.set_thumbnail(url=avatar_url.url)

            # IDs & names
            embed.add_field(name="Username", value=f"{subject}", inline=True)
            embed.add_field(name="ID", value=f"`{subject.id}`", inline=True)

            # Account creation time
            created = getattr(subject, "created_at", None)
            if created:
                embed.add_field(
                    name="Account Created",
                    value=f"{discord.utils.format_dt(created, style='F')}\n{discord.utils.format_dt(created, style='R')}",
                    inline=False
                )
            else:
                embed.add_field(name="Account Created", value="Unknown", inline=False)

            # If member (in guild) show server-specific info
            if member:
                joined = getattr(member, "joined_at", None)
                if joined:
                    embed.add_field(
                        name="Joined Server",
                        value=f"{discord.utils.format_dt(joined, style='F')}\n{discord.utils.format_dt(joined, style='R')}",
                        inline=False
                    )
                else:
                    embed.add_field(name="Joined Server", value="Unknown", inline=False)

                # Roles (exclude @everyone)
                roles: List[discord.Role] = [r for r in member.roles if r.name != "@everyone"]
                roles_sorted = sorted(roles, key=lambda r: r.position, reverse=True)
                roles_text = ", ".join(r.mention for r in roles_sorted[:25])  # don't exceed Discord limits
                if len(roles_sorted) > 25:
                    roles_text += f", ... and {len(roles_sorted)-25} more"
                embed.add_field(name=f"Roles ({len(roles_sorted)})", value=roles_text or "None", inline=False)

                # Top role and color
                top = member.top_role
                embed.add_field(name="Top Role", value=top.mention if top else "None", inline=True)
                embed.add_field(name="Hoist/Display", value=str(top.hoist) if top else "N/A", inline=True)

                # Display current status / activity if present
                status = getattr(member, "status", None)
                status_str = str(status).title() if status else "Unknown"
                activity = None
                if member.activities:
                    # pick the most relevant activity (first non-empty)
                    for a in member.activities:
                        try:
                            if getattr(a, "name", None):
                                activity = f"{a.type.name.title() if hasattr(a, 'type') else 'Activity'}: {getattr(a, 'name', str(a))}"
                                break
                        except Exception:
                            continue
                embed.add_field(name="Status", value=status_str, inline=True)
                embed.add_field(name="Activity", value=activity or "None", inline=True)

            else:
                # Not a member (e.g., DM or user not in guild)
                embed.add_field(name="Server Info", value="Not a member of this server or command used in DMs.", inline=False)

            # Is bot?
            embed.add_field(name="Bot?", value=str(subject.bot), inline=True)

            # Footer + requester
            footer_icon = getattr(requestor, "display_avatar", None)
            embed.set_footer(text=f"Requested by {getattr(requestor, 'display_name', str(requestor))}", icon_url=footer_icon.url if footer_icon else None)

            # Send response
            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except Exception as exc:
            # Friendly error message; ephemeral if slash
            err = discord.Embed(title="Error", description="Failed to fetch user info.", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            err.add_field(name="Details", value=str(exc)[:1000], inline=False)
            if is_interaction:
                await ctx.response.send_message(embed=err, ephemeral=True)
            else:
                await ctx.send(embed=err)


async def setup(bot: commands.Bot):
    await bot.add_cog(Whois(bot))
