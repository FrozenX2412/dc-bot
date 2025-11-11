# cogs/util/calc.py
import ast
import operator
from typing import Union

import discord
from discord.ext import commands

ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Safety limits
MAX_EXPONENT = 10          # disallow x ** y where y > MAX_EXPONENT (absolute)
MAX_RESULT = 1e12          # disallow extremely large results
MAX_NODES = 200            # avoid very deep/large ASTs


class SafeCalcError(Exception):
    pass


class Calculator(commands.Cog):
    """Safe calculator with hybrid command (prefix + slash)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="calc", description="Evaluate a safe math expression")
    async def calc(self, ctx: Union[commands.Context, discord.Interaction], *, expression: str):
        """
        Example: /calc expression: "2 + 3*(4-1)"
        Works as both a prefix and a slash command.
        """
        is_interaction = isinstance(ctx, discord.Interaction)
        # If hybrid invoked as an Interaction, discord.py usually passes a Context, but handle both.
        try:
            expression = expression.strip()
            if not expression:
                raise SafeCalcError("Empty expression.")

            # Parse to AST
            try:
                node = ast.parse(expression, mode="eval")
            except SyntaxError as se:
                raise SafeCalcError("Syntax error in expression.") from se

            # Basic node count limit
            all_nodes = list(ast.walk(node))
            if len(all_nodes) > MAX_NODES:
                raise SafeCalcError("Expression too complex.")

            result = self._eval_node(node.body)

            # Enforce result magnitude limit
            if isinstance(result, (int, float)) and abs(result) > MAX_RESULT:
                raise SafeCalcError("Result too large to display.")

            # Build and send embed
            embed = discord.Embed(title="🧮 Calculator", color=discord.Color.green())
            embed.add_field(name="Expression", value=f"```{expression}```", inline=False)
            embed.add_field(name="Result", value=f"```{result}```", inline=False)
            requester = ctx.user.display_name if is_interaction else ctx.author.display_name
            embed.set_footer(text=f"Requested by {requester}")

            if is_interaction:
                if not ctx.response.is_done():
                    await ctx.response.send_message(embed=embed)
                else:
                    await ctx.followup.send(embed=embed)
            else:
                await ctx.send(embed=embed)

        except SafeCalcError as e:
            err_embed = discord.Embed(title="Calculation error", description=str(e), color=discord.Color.red())
            err_embed.add_field(name="Allowed operators", value="`+  -  *  /  //  %  **` and parentheses", inline=False)
            err_embed.set_footer(text="Examples: 2+2, (3+4)*5, 2**3")
            if is_interaction:
                try:
                    if not ctx.response.is_done():
                        await ctx.response.send_message(embed=err_embed, ephemeral=True)
                    else:
                        await ctx.followup.send(embed=err_embed, ephemeral=True)
                except Exception:
                    if ctx.channel:
                        await ctx.channel.send(embed=err_embed)
            else:
                await ctx.send(embed=err_embed)
        except Exception as exc:
            # Unexpected error — don't leak internals to users
            err_embed = discord.Embed(title="Error", description="An internal error occurred.", color=discord.Color.red())
            if is_interaction:
                try:
                    if not ctx.response.is_done():
                        await ctx.response.send_message(embed=err_embed, ephemeral=True)
                    else:
                        await ctx.followup.send(embed=err_embed, ephemeral=True)
                except Exception:
                    if ctx.channel:
                        await ctx.channel.send(embed=err_embed)
            else:
                await ctx.send(embed=err_embed)

    def _eval_node(self, node):
        """Recursively evaluate a whitelisted AST node."""
        # Numbers (Constant for py3.8+)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise SafeCalcError("Only numeric constants are allowed.")

        # Support legacy Num node (just in case)
        if isinstance(node, ast.Num):
            return node.n

        # Parenthesis/grouping are represented by the sub-node already (no separate node)

        # Unary ops
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_UNARYOPS:
                raise SafeCalcError("Unsupported unary operator.")
            val = self._eval_node(node.operand)
            return ALLOWED_UNARYOPS[op_type](val)

        # Binary ops
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_BINOPS:
                raise SafeCalcError("Unsupported binary operator.")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            # Exponent safety: limit exponent magnitude
            if op_type is ast.Pow:
                try:
                    if abs(right) > MAX_EXPONENT:
                        raise SafeCalcError(f"Exponent too large (max {MAX_EXPONENT}).")
                except TypeError:
                    raise SafeCalcError("Invalid exponent.")

            try:
                return ALLOWED_BINOPS[op_type](left, right)
            except ZeroDivisionError:
                raise SafeCalcError("Division by zero.")
            except Exception:
                raise SafeCalcError("Error evaluating expression.")

        # Parenthesized expression or nested expression handled by AST structure

        # Reject any other node types explicitly (Name, Call, Attribute, Subscript, etc.)
        raise SafeCalcError("Unsupported expression element detected (only numbers and basic operators allowed).")


async def setup(bot: commands.Bot):
    await bot.add_cog(Calculator(bot))
