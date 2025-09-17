"""
Discord bot for Politics & War
Handles Discord interactions and commands
"""

import discord
from discord.ext import commands
import os
import asyncio
from api.pnw_api import PoliticsAndWarAPI
from utils.espionage_monitor import EspionageMonitor
from database.espionage_tracker import EspionageTracker

class DiscordBot:
    """Discord bot for Politics & War interactions"""
    
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        self.api_key = os.getenv('PNW_API_KEY')
        
        # Set up bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Initialize bot
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Initialize API (defensive initialization)
        if self.api_key:
            try:
                self.pnw_api = PoliticsAndWarAPI(self.api_key)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize API: {e}")
                self.pnw_api = None
        else:
            print("⚠️ Warning: PNW_API_KEY not set, API features disabled")
            self.pnw_api = None
        
        # Initialize espionage monitoring system
        if self.pnw_api:
            try:
                self.espionage_monitor = EspionageMonitor(self.api_key)
                self.espionage_tracker = EspionageTracker()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize monitoring system: {e}")
                self.espionage_monitor = None
                self.espionage_tracker = None
        else:
            print("⚠️ Warning: Monitoring system disabled (no API key)")
            self.espionage_monitor = None
            self.espionage_tracker = None
        
        # Start 24/7 monitoring in background
        self.monitoring_task = None
        
        # Add event handlers
        self.setup_events()
        self.setup_commands()
    
    def setup_events(self):
        """Set up bot events"""
        
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has connected to Discord!')
            print(f'Bot is in {len(self.bot.guilds)} guilds')
            
            # Automatically start 24/7 monitoring
            print("🚀 Auto-starting 24/7 espionage monitoring...")
            if not self.monitoring_task or self.monitoring_task.done():
                self.monitoring_task = asyncio.create_task(self.espionage_monitor.start_24_7_monitoring())
                print("✅ 24/7 monitoring started automatically")
    
    def setup_commands(self):
        """Set up bot commands"""
        
        @self.bot.command(name='nation')
        async def get_nation_info(ctx, *, nation_name: str = None):
            """Get information about a nation"""
            try:
                if nation_name:
                    # Search for nation by name
                    result = self.pnw_api.search_nations(name=nation_name)
                else:
                    # Get own nation info
                    result = self.pnw_api.get_nation()
                
                if 'errors' in result:
                    await ctx.send(f"Error: {result['errors'][0]['message']}")
                    return
                
                # Format and send response
                if nation_name:
                    nations = result.get('data', {}).get('nations', {}).get('data', [])
                    if not nations:
                        await ctx.send(f"No nation found with name: {nation_name}")
                        return
                    nation_data = nations[0]
                else:
                    nation_data = result.get('data', {}).get('me', {}).get('nation', {})
                
                embed = discord.Embed(
                    title=f"Nation: {nation_data.get('nation_name', 'Unknown')}",
                    color=0x00ff00
                )
                embed.add_field(name="Leader", value=nation_data.get('leader_name', 'Unknown'), inline=True)
                embed.add_field(name="Score", value=nation_data.get('score', 'Unknown'), inline=True)
                
                alliance = nation_data.get('alliance', {})
                if alliance:
                    embed.add_field(name="Alliance", value=alliance.get('name', 'None'), inline=True)
                
                cities = nation_data.get('cities', [])
                if cities:
                    embed.add_field(name="Cities", value=len(cities), inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='gameinfo')
        async def get_game_info(ctx):
            """Get current game information"""
            try:
                result = self.pnw_api.get_game_info()
                
                if 'errors' in result:
                    await ctx.send(f"Error: {result['errors'][0]['message']}")
                    return
                
                game_info = result.get('data', {}).get('game_info', {})
                
                embed = discord.Embed(
                    title="Politics & War Game Info",
                    color=0x0099ff
                )
                embed.add_field(name="Game Date", value=game_info.get('game_date', 'Unknown'), inline=False)
                
                radiation = game_info.get('radiation', {})
                if radiation:
                    embed.add_field(name="Global Radiation", value=radiation.get('global', 'Unknown'), inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Show all available commands"""
            embed = discord.Embed(
                title="🤖 Politics & War Bot Commands",
                description="Available commands for espionage monitoring and game info",
                color=0x0099ff
            )
            
            # Basic commands
            embed.add_field(
                name="📊 Basic Commands",
                value="`!ping` - Check bot status\n"
                      "`!gameinfo` - Get game information\n"
                      "`!nation <name>` - Get nation info",
                inline=False
            )
            
            # Spy commands
            embed.add_field(
                name="🕵️ Espionage Commands",
                value="`!spy [nation]` - Check spy activity\n"
                      "`!spycheck [nation]` - Detailed spy status\n"
                      "`!wars [nation]` - Show active wars\n"
                      "`!checknation <name>` - Manual nation check",
                inline=False
            )
            
            # Monitoring commands
            embed.add_field(
                name="🔍 24/7 Monitoring System",
                value="`!monitor` - System status\n"
                      "`!resets [alliance]` - Show reset times\n"
                      "`!startmonitor` - Start 24/7 monitoring (Admin)\n"
                      "`!stopmonitor` - Stop monitoring (Admin)\n"
                      "`!collect` - Index all nations (Admin)",
                inline=False
            )
            
            embed.add_field(
                name="💡 24/7 System Features",
                value="• **Auto-starts** when bot connects\n"
                      "• **Indexes all nations** in the game first\n"
                      "• **Skips vacation mode** nations\n"
                      "• **Only monitors alliance members**\n"
                      "• **Stops monitoring** once reset time found\n"
                      "• **Auto-adds new nations** every hour",
                inline=False
            )
            
            embed.add_field(
                name="💡 Tips",
                value="• Commands without `[nation]` use your nation\n"
                      "• Use nation names or IDs\n"
                      "• Reset times help predict daily reset schedules",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='ping')
        async def ping(ctx):
            """Check if the bot is responsive"""
            await ctx.send(f'Pong! Latency: {round(self.bot.latency * 1000)}ms')
        
        @self.bot.command(name='spy')
        async def check_spy_activity(ctx, *, nation_name: str = None):
            """Check spy activity for a nation"""
            try:
                if nation_name:
                    # Search for nation first to get ID
                    search_result = self.pnw_api.search_nations(name=nation_name)
                    if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                        await ctx.send(f"Nation '{nation_name}' not found.")
                        return
                    
                    nation_data = search_result['data']['nations']['data'][0]
                    nation_id = nation_data['id']
                    result = self.pnw_api.get_spy_activity(nation_id)
                else:
                    result = self.pnw_api.get_spy_activity()
                
                if 'errors' in result:
                    await ctx.send(f"Error: {result['errors'][0]['message']}")
                    return
                
                # Extract nation data
                if nation_name:
                    nation_data = result.get('data', {}).get('nations', {}).get('data', [{}])[0]
                else:
                    nation_data = result.get('data', {}).get('me', {}).get('nation', {})
                
                embed = discord.Embed(
                    title=f"🕵️ Spy Activity: {nation_data.get('nation_name', 'Unknown')}",
                    color=0x800080
                )
                
                spy_casualties = nation_data.get('spy_casualties', 0)
                spy_kills = nation_data.get('spy_kills', 0)
                spy_attacks = nation_data.get('spy_attacks', 0)
                espionage_available = nation_data.get('espionage_available', False)
                
                embed.add_field(name="Spies Lost", value=spy_casualties, inline=True)
                embed.add_field(name="Spies Killed", value=spy_kills, inline=True)
                embed.add_field(name="Spy Attacks Made", value=spy_attacks, inline=True)
                embed.add_field(name="Espionage Available", value="✅ Yes" if espionage_available else "❌ No", inline=True)
                
                # Add interpretation
                if spy_casualties > 0:
                    embed.add_field(name="Recent Activity", value="⚠️ This nation has lost spies recently", inline=False)
                elif spy_kills > 0:
                    embed.add_field(name="Defense Status", value="🛡️ This nation has killed enemy spies", inline=False)
                
                if not espionage_available:
                    embed.add_field(name="Status", value="🛡️ Protected from espionage operations", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='spycheck')
        async def check_espionage_status(ctx, *, nation_name: str = None):
            """Check if a nation can be spied on and their recent activity"""
            try:
                if nation_name:
                    # Search for nation first
                    search_result = self.pnw_api.search_nations(name=nation_name)
                    if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                        await ctx.send(f"Nation '{nation_name}' not found.")
                        return
                    
                    nation_data = search_result['data']['nations']['data'][0]
                    nation_id = nation_data['id']
                    result = self.pnw_api.check_espionage_status(nation_id)
                else:
                    result = self.pnw_api.check_espionage_status()
                
                if 'errors' in result:
                    await ctx.send(f"Error: {result['errors'][0]['message']}")
                    return
                
                # Extract nation data
                if nation_name:
                    nation_data = result.get('data', {}).get('nations', {}).get('data', [{}])[0]
                else:
                    nation_data = result.get('data', {}).get('me', {}).get('nation', {})
                
                embed = discord.Embed(
                    title=f"🔍 Espionage Status: {nation_data.get('nation_name', 'Unknown')}",
                    color=0x4B0082
                )
                
                espionage_available = nation_data.get('espionage_available', False)
                beige_turns = nation_data.get('beige_turns', 0)
                vmode_turns = nation_data.get('vacation_mode_turns', 0)
                spy_casualties = nation_data.get('spy_casualties', 0)
                last_active = nation_data.get('last_active', 'Unknown')
                
                # Main status
                if espionage_available:
                    embed.add_field(name="Espionage Status", value="✅ Available for espionage", inline=False)
                else:
                    embed.add_field(name="Espionage Status", value="❌ Protected from espionage", inline=False)
                
                # Protection reasons
                protection_reasons = []
                if beige_turns > 0:
                    protection_reasons.append(f"Beige protection ({beige_turns} turns left)")
                if vmode_turns > 0:
                    protection_reasons.append(f"Vacation mode ({vmode_turns} turns left)")
                
                if protection_reasons:
                    embed.add_field(name="Protection", value="\n".join(protection_reasons), inline=False)
                
                # Recent spy activity
                if spy_casualties > 0:
                    embed.add_field(name="⚠️ Recent Spy Activity", value=f"Lost {spy_casualties} spies recently", inline=False)
                
                embed.add_field(name="Last Active", value=last_active, inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='wars')
        async def check_active_wars(ctx, *, nation_name: str = None):
            """Check active wars for a nation"""
            try:
                if nation_name:
                    # Search for nation first
                    search_result = self.pnw_api.search_nations(name=nation_name)
                    if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                        await ctx.send(f"Nation '{nation_name}' not found.")
                        return
                    
                    nation_data = search_result['data']['nations']['data'][0]
                    nation_id = nation_data['id']
                    result = self.pnw_api.get_active_wars(nation_id)
                else:
                    result = self.pnw_api.get_active_wars()
                
                if 'errors' in result:
                    await ctx.send(f"Error: {result['errors'][0]['message']}")
                    return
                
                # Extract wars data
                if nation_name:
                    wars = result.get('data', {}).get('wars', {}).get('data', [])
                    display_name = nation_name
                else:
                    nation_data = result.get('data', {}).get('me', {}).get('nation', {})
                    wars = nation_data.get('wars', [])
                    display_name = nation_data.get('nation_name', 'Your nation')
                
                if not wars:
                    await ctx.send(f"🕊️ {display_name} is not currently in any active wars.")
                    return
                
                embed = discord.Embed(
                    title=f"⚔️ Active Wars: {display_name}",
                    description=f"Currently involved in {len(wars)} war(s)",
                    color=0xFF0000
                )
                
                for war in wars[:5]:  # Limit to 5 wars to avoid embed size limits
                    war_id = war.get('id', 'Unknown')
                    attacker = war.get('attacker', {}).get('nation_name', 'Unknown')
                    defender = war.get('defender', {}).get('nation_name', 'Unknown')
                    turns_left = war.get('turns_left', 'Unknown')
                    reason = war.get('reason', 'No reason given')
                    
                    war_info = f"**Attacker:** {attacker}\n**Defender:** {defender}\n**Turns Left:** {turns_left}\n**Reason:** {reason[:100]}..."
                    embed.add_field(name=f"War #{war_id}", value=war_info, inline=False)
                
                if len(wars) > 5:
                    embed.add_field(name="Note", value=f"Showing 5 of {len(wars)} wars", inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='monitor')
        async def monitor_status(ctx):
            """Check the espionage monitoring system status"""
            try:
                stats = self.espionage_monitor.get_monitoring_stats()
                
                embed = discord.Embed(
                    title="🔍 24/7 Espionage Monitoring System",
                    color=0x9932CC
                )
                
                # System status
                status_emoji = "🟢" if stats.get('is_running', False) else "🔴"
                monitoring_emoji = "🟢" if stats.get('monitoring_active', False) else "🔴"
                
                embed.add_field(
                    name="System Status", 
                    value=f"{status_emoji} {'Running' if stats.get('is_running', False) else 'Stopped'}", 
                    inline=True
                )
                
                embed.add_field(
                    name="Monitoring Status", 
                    value=f"{monitoring_emoji} {'Active' if stats.get('monitoring_active', False) else 'Inactive'}", 
                    inline=True
                )
                
                # Database stats
                embed.add_field(name="Nations Tracked", value=f"{stats.get('total_nations', 0):,}", inline=True)
                embed.add_field(name="Currently Monitoring", value=f"{stats.get('monitoring_count', 0):,}", inline=True)
                embed.add_field(name="Reset Times Detected", value=f"{stats.get('reset_times_detected', 0):,}", inline=True)
                embed.add_field(name="Recent Checks (24h)", value=f"{stats.get('recent_checks_24h', 0):,}", inline=True)
                
                # Last scan info
                last_scan = stats.get('last_full_scan')
                if last_scan:
                    embed.add_field(name="Last Full Scan", value=last_scan, inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='startmonitor')
        @commands.has_permissions(administrator=True)
        async def start_monitoring(ctx):
            """Start the 24/7 espionage monitoring system (Admin only)"""
            try:
                if self.espionage_monitor.is_running:
                    await ctx.send("⚠️ Monitoring system is already running!")
                    return
                
                await ctx.send("🚀 Starting 24/7 espionage monitoring system...")
                await ctx.send("📊 Phase 1: Indexing all nations...")
                
                # Start 24/7 monitoring in background
                if not self.monitoring_task or self.monitoring_task.done():
                    self.monitoring_task = asyncio.create_task(self.espionage_monitor.start_24_7_monitoring())
                
                await ctx.send("✅ 24/7 monitoring system started!\n"
                              "• All nations will be indexed first\n"
                              "• Only alliance members will be monitored\n"
                              "• Vacation mode nations will be skipped\n"
                              "• Monitoring stops once reset time is found")
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='stopmonitor')
        @commands.has_permissions(administrator=True)
        async def stop_monitoring(ctx):
            """Stop the monitoring system (Admin only)"""
            try:
                if not self.espionage_monitor.is_running:
                    await ctx.send("⚠️ Monitoring system is not running!")
                    return
                
                self.espionage_monitor.stop_monitoring()
                
                if self.monitoring_task and not self.monitoring_task.done():
                    self.monitoring_task.cancel()
                
                await ctx.send("🛑 Monitoring system stopped!")
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='collect')
        @commands.has_permissions(administrator=True)
        async def collect_nations(ctx):
            """Index all nations in the game (Admin only)"""
            try:
                await ctx.send("�️ Starting full nation indexing... This may take 10-15 minutes.")
                await ctx.send("📊 Indexing all nations in the game (alliance members only)...")
                
                result = await self.espionage_monitor.index_all_nations()
                
                if result.get('success'):
                    embed = discord.Embed(
                        title="✅ Nation Indexing Complete",
                        color=0x00FF00
                    )
                    embed.add_field(name="Total Nations Processed", value=f"{result.get('total_nations', 0):,}", inline=True)
                    embed.add_field(name="Alliance Nations Indexed", value=f"{result.get('alliance_nations', 0):,}", inline=True)
                    
                    # Get current monitoring stats
                    stats = self.espionage_monitor.get_monitoring_stats()
                    embed.add_field(name="Now Monitoring", value=f"{stats.get('monitoring_count', 0):,}", inline=True)
                    
                    embed.add_field(
                        name="ℹ️ Note", 
                        value="• Vacation mode nations were skipped\n"
                              "• Only alliance members are monitored\n"
                              "• Monitoring will find daily reset times", 
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title="❌ Indexing Failed",
                        description=f"Error: {result.get('error', 'Unknown error')}",
                        color=0xFF0000
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='resets')
        async def show_reset_times(ctx, *, alliance_name: str = None):
            """Show detected reset times for an alliance or all"""
            try:
                # If alliance name provided, find the alliance
                alliance_id = None
                if alliance_name:
                    search_result = self.pnw_api.query(f'{{alliances(name:["{alliance_name}"]){{data{{id name}}}}}}')
                    if search_result.get('data', {}).get('alliances', {}).get('data'):
                        alliance_id = search_result['data']['alliances']['data'][0]['id']
                    else:
                        await ctx.send(f"Alliance '{alliance_name}' not found.")
                        return
                
                report = await self.espionage_monitor.get_reset_time_report(alliance_id)
                
                if 'error' in report:
                    await ctx.send(f"Error generating report: {report['error']}")
                    return
                
                embed = discord.Embed(
                    title=f"🕐 Reset Times Report{' - ' + alliance_name if alliance_name else ''}",
                    color=0x4169E1
                )
                
                embed.add_field(name="Total Detections", value=f"{report.get('total_reset_times_detected', 0):,}", inline=True)
                embed.add_field(name="Unique Nations", value=f"{report.get('unique_nations_with_resets', 0):,}", inline=True)
                
                # Show hourly distribution
                hourly = report.get('hourly_distribution', {})
                if hourly:
                    top_hours = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:5]
                    hour_text = "\n".join([f"{hour:02d}:00 - {count} resets" for hour, count in top_hours])
                    embed.add_field(name="Peak Reset Hours (UTC)", value=hour_text, inline=False)
                
                # Show recent detections
                recent = report.get('recent_detections', [])
                if recent:
                    recent_text = "\n".join([
                        f"**{det['nation_name']}** - {det['reset_time'][:16]}" 
                        for det in recent[-5:]
                    ])
                    embed.add_field(name="Recent Detections", value=recent_text, inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        
        @self.bot.command(name='checknation')
        async def check_specific_nation(ctx, *, nation_name: str):
            """Manually check a specific nation's espionage status"""
            try:
                # Find the nation
                search_result = self.pnw_api.search_nations(name=nation_name)
                if 'errors' in search_result or not search_result.get('data', {}).get('nations', {}).get('data', []):
                    await ctx.send(f"Nation '{nation_name}' not found.")
                    return
                
                nation_data = search_result['data']['nations']['data'][0]
                nation_id = nation_data['id']
                
                await ctx.send(f"🔍 Checking {nation_name}...")
                
                # Manual check
                result = await self.espionage_monitor.manual_check_nation(nation_id)
                
                if result.get('success'):
                    await ctx.send(f"✅ Successfully checked {nation_name}")
                    
                    # Get current status
                    spy_result = self.pnw_api.check_espionage_status(nation_id)
                    if spy_result.get('data'):
                        nation_info = spy_result['data']['nations']['data'][0]
                        
                        embed = discord.Embed(
                            title=f"🔍 Current Status: {nation_name}",
                            color=0x9932CC
                        )
                        
                        espionage_available = nation_info.get('espionage_available', True)
                        embed.add_field(
                            name="Espionage Available", 
                            value="✅ Yes" if espionage_available else "❌ No", 
                            inline=True
                        )
                        
                        if not espionage_available:
                            beige = nation_info.get('beige_turns', 0)
                            vmode = nation_info.get('vacation_mode_turns', 0)
                            if beige > 0:
                                embed.add_field(name="Protection", value=f"Beige ({beige} turns)", inline=True)
                            elif vmode > 0:
                                embed.add_field(name="Protection", value=f"Vacation ({vmode} turns)", inline=True)
                        
                        await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ Error checking {nation_name}: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
    
    async def start(self):
        """Start the Discord bot"""
        if not self.token:
            print("Error: DISCORD_TOKEN not found in environment variables")
            return
        
        try:
            await self.bot.start(self.token)
        except Exception as e:
            print(f"Error starting Discord bot: {e}")
