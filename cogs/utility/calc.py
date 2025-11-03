import discord
from discord.ext import commands
from discord import app_commands
import re
import ast
import operator

class Calculator(commands.Cog):
    """Simple calculator command with safety checks"""
    
    def __init__(self, bot):
        self.bot = bot
        # Safe operators for calculation
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.UAdd: operator.pos,
            ast.USub: operator.neg
        }
    
    @commands.command(name='calc', aliases=['calculate', 'math'])
    async def calc_prefix(self, ctx, *, expression: str):
        """Calculate a mathematical expression (prefix command)"""
        await self._calculate(ctx, expression)
    
    @app_commands.command(name='calc', description='Calculate a mathematical expression')
    async def calc_slash(self, interaction: discord.Interaction, expression: str):
        """Calculate a mathematical expression (slash command)"""
        await self._calculate(interaction, expression)
    
    async def _calculate(self, ctx_or_interaction, expression: str):
        """Internal method to perform safe calculation"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        
        try:
            # Remove any whitespace
            expression = expression.strip()
            
            # Perform safe evaluation
            result = self._eval_expr(expression)
            
            # Create embed
            embed = discord.Embed(
                title="🧮 Calculator",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Expression", value=f"```{expression}```", inline=False)
            embed.add_field(name="Result", value=f"```{result}```", inline=False)
            embed.set_footer(text=f"Requested by {ctx_or_interaction.user.display_name if is_interaction else ctx_or_interaction.author.display_name}")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
                
        except (ValueError, SyntaxError, KeyError) as e:
            error_embed = discord.Embed(
                title="Calculation Error",
                description=f"Invalid expression: {str(e)}",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Expression",
                value=f"```{expression}```",
                inline=False
            )
            error_embed.set_footer(text="Please use basic mathematical operators: +, -, *, /, **, %, ( )")
            
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description=f"Failed to calculate: {str(e)}",
                color=discord.Color.red()
            )
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=error_embed, ephemeral=True)
            else:
                await ctx_or_interaction.send(embed=error_embed)
    
    def _eval_expr(self, expr):
        """Safely evaluate mathematical expression"""
        # Parse the expression
        node = ast.parse(expr, mode='eval')
        return self._eval_node(node.body)
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes"""
        if isinstance(node, ast.Constant):  # Number
            return node.value
        elif isinstance(node, ast.BinOp):  # Binary operation
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):  # Unary operation
            operand = self._eval_node(node.operand)
            return self.operators[type(node.op)](operand)
        else:
            raise ValueError("Unsupported operation")

async def setup(bot):
    await bot.add_cog(Calculator(bot))
