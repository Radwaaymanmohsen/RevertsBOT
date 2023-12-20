import discord
from discord.ext import commands
from datetime import datetime, date, timedelta
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd 
import asyncio
from math import floor



connection = sqlite3.connect("db/new_reverts_database.db")
activity_conn = sqlite3.connect("activity.db")
#connection = sqlite3.connect("test.db")
 
cr = connection.cursor()
activitycr = activity_conn.cursor()
counter = 0

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('rev_bot.json', scope)

client = gspread.authorize(creds)
sheet = client.open('Reverts_Tracker').sheet1


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.add_cog(MyCog(bot))
 

class Menu(discord.ui.View):
    def __init__(self, mem: discord.Member | discord.User, notes = None):
        self.mem = mem
        self.notes = notes
        super().__init__()

    @discord.ui.select(
        placeholder="Select status",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Revert", value="revert"),
            discord.SelectOption(label="At Risk", value="atrisk"),
            discord.SelectOption(label="Interested in Islam", value="interested"),
        ],
        
    )
    async def select_status(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        if isinstance(self.mem, discord.Member):
            is_male = discord.utils.get(self.mem.roles, id=884923006319734814) is not None

            if select.values[0] in ["revert", "atrisk", "interested"]:
                cr.execute(
                        f"""
                            INSERT INTO REVERTS (revert_id, gender, state, mod_id, notes, date) VALUES (?, ?, ?, ?, ?, datetime('now'));
                        """,
                        (self.mem.id, "Male" if is_male else "Female",select.values[0], interaction.user.id, self.notes),
                    )
                connection.commit()

            # hdcr.execute(f"""
            #         SELECT * FROM RESPONSE WHERE id = ?
            
            # """,(counter))
            # hdrow = hdcr.fetchone()

            #await interaction.response.send_message(f"✅ **Added user successfully**")
            await interaction.response.send_message(f"✅** JAZAKUM ALLAHU KHAYRAN **")

            
            #await delete_original_response()
            # await interaction.delete_original_response()
            await interaction.message.delete()
            
            
            self.stop()

        else :
            if select.values[0] in ["revert", "atrisk", "interested"]:
                    cr.execute(
                        f"""
                            UPDATE REVERTS 
                            SET state =? , mod_id =?, notes = ? , date= datetime('now') 
                            WHERE revert_id = ? ;
                        """,
                        (select.values[0], interaction.user.id, self.notes, self.mem.id),
                    )
                    connection.commit()

            #await interaction.response.send_message(f"✅ **Added user successfully**")
            await interaction.response.send_message(f"✅** JAZAKUM ALLAHU KHAYRAN **")

            await interaction.message.delete()

                
            self.stop()


class MenuUpdate(discord.ui.View):
    def __init__(self, mem: discord.Member | discord.User , notes = None):
        self.mem = mem
        self.notes = notes
        super().__init__()

    @discord.ui.select(
        placeholder="Select state",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Revert", value="revert"),
            discord.SelectOption(label="At Risk", value="atrisk"),
            discord.SelectOption(label="Interested in Islam", value="interested"),
        ],
    )
    async def select_status(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):


        cr.execute(
            f"""
                UPDATE REVERTS 
                SET mod_id = ? , notes = ? , state =?, date = datetime('now')
                WHERE revert_id = ? 
            """,
            (
                interaction.user.id,
                self.notes,
                select.values[0],
                self.mem.id,
            ), 
        )
        cr.execute(
            "INSERT INTO HISTORY (revert_id, mod_id, notes, state, date) VALUES (?,?,?,?, datetime('now'))",
            (self.mem.id, interaction.user.id, self.notes, select.values[0]),
        )

        connection.commit()

        #await interaction.response.send_message(f"✅ **The user has been updated successfully !**")
        await interaction.response.send_message(f"✅** JAZAKUM ALLAHU KHAYRAN **")

        await interaction.message.delete()

        self.stop()

class MenuGender(discord.ui.View):
    def __init__(self, user: discord.User, notes = None):
        self.user = user
        self.notes = notes
        super().__init__()

    @discord.ui.select(
        placeholder="Select gender",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Female", value="Female"),
            discord.SelectOption(label="Male", value="Male"),
        ],
    )
    async def select_status(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):


        if select.values[0] in ["Male", "Female"]:
            
            cr.execute(
                    f"""
                        INSERT INTO REVERTS (revert_id, gender, inserver) VALUES (?, ?, 'No');
                    """,
                    (self.user.id, select.values[0]),
                )
            connection.commit()

        #await interaction.response.send_message(f"What is the user state ?")
        await interaction.message.delete()

        self.stop()


class MyCog(commands.Cog, name="btengan"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return True
        return await commands.has_role(884918189727825960).predicate(ctx) or  commands.has_role(920740162437283932).predicate(ctx) or commands.has_role(987191130745610271).predicate(ctx) 

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, commands.MissingRole):
            embed = discord.Embed(description="❌ **Sorry you are not a mod **", color=discord.Color.red())
            await ctx.send(embed=embed)

        elif isinstance(err, commands.MissingRequiredArgument):
            embed = discord.Embed(description="❌ **You didn't provide the user **", color=discord.Color.red())
            await ctx.send(embed=embed)

        else:
            raise err

    @commands.command()
    async def add(self, ctx: commands.Context, mem: discord.Member | discord.User, *, notes=None):
        if isinstance(mem, discord.Member):
                is_male = discord.utils.get(mem.roles, id=884923006319734814) != None
                username = mem.global_name or str(mem)
        
                cr.execute(
                    f"""
                    SELECT * FROM REVERTS WHERE revert_id = ? ;
                    """,
                    (mem.id,),
                )
                row = cr.fetchone()
                #notes = row[6]
                if row is not None:
                    #embed = discord.Embed(description="**This user has been recorded already ** ", color=discord.Color.red())
                    #await ctx.send(embed=embed)
                    ##################################
                    notes = notes or row[5]
                    view = MenuUpdate(mem, notes)
                    await ctx.send(view=view)    
                    await view.wait()

                    try:
                        cr.execute("SELECT * FROM REVERTS WHERE revert_id = ?", (mem.id,))
                        row = cr.fetchone()

                        if row:
                            cell = sheet.find (str(mem.id))

                            col_mod_name = cell.col+4
                            col_date = cell.col+5
                            col_notes = cell.col+6
                            col_state = cell.col+3

                            sheet.update_cell(cell.row, col_mod_name, ctx.author.name)  #updating mod_name
                            sheet.update_cell(cell.row, col_date, row[4])           #updating date
                            sheet.update_cell(cell.row, col_notes,row[5])             #updating notes 
                            sheet.update_cell(cell.row, col_state,row[6])            #update state
                        
                        else:
                            print("Row not found for mem.id:", mem.id)

                    except gspread.exceptions.APIError as e:
                        print(f"Google Sheets API Error: {e}")

                    except sqlite3.Error as e:
                        print(f"SQLite Error: {e}")
                        ################################################################

                    return

                view = Menu(mem,notes)
                await ctx.send(view=view)    
                await view.wait()

                ## google sheet 
                try :
                    cr.execute("SELECT * FROM REVERTS WHERE revert_id=?", (mem.id,))
                    row = cr.fetchone()
                    print(row)
                    cols = [str(row[1]),mem.name,row[2],row[6],ctx.author.name,row[4],row[5]]

                    sheet.append_row(cols)
                
                except gspread.exceptions.APIError as e:
                    print(f"Google Sheets API Error: {e}")

                ################################
                cr.execute(
                        f"""
                                    INSERT INTO HISTORY (revert_id, state, mod_id, notes, date) VALUES (?, ?, ?, ?, datetime('now'));
                                """,
                                (row[1],row[6],row[3], row[5]),
                            )   

                connection.commit()

                # embed = discord.Embed(description="✅ **Added user successfully**", color=discord.Color.green())
                # await ctx.send(embed=embed)

        else:
            cr.execute(
                f"""
                SELECT * FROM REVERTS WHERE revert_id = ? ;
                """,
                (mem.id,),
            )
            row = cr.fetchone()

            if row is not None:
                    notes = notes or row[5]
                    view = MenuUpdate(mem, notes)
                    await ctx.send(view=view)    
                    await view.wait()

                    try:
                        cr.execute("SELECT * FROM REVERTS WHERE revert_id = ?", (mem.id,))
                        row = cr.fetchone()

                        if row:
                            cell = sheet.find (str(mem.id))

                            col_mod_name = cell.col+4
                            col_date = cell.col+5
                            col_notes = cell.col+6
                            col_state = cell.col+3

                            sheet.update_cell(cell.row, col_mod_name, ctx.author.name)  #updating mod_name
                            sheet.update_cell(cell.row, col_date, row[4])           #updating date
                            sheet.update_cell(cell.row, col_notes,row[5])             #updating notes 
                            sheet.update_cell(cell.row, col_state,row[6])            #update state
                        
                        else:
                            print("Row not found for mem.id:", mem.id)

                    except gspread.exceptions.APIError as e:
                        print(f"Google Sheets API Error: {e}")

                    except sqlite3.Error as e:
                        print(f"SQLite Error: {e}")
                        ################################################################

                    return

            
            view = MenuGender(mem)
            view2= Menu(mem,notes)
            await ctx.send(view=view) 
            await view.wait()   
            await ctx.send(view=view2)
            await view2.wait()
            ##################
            cr.execute(
                f"""
                SELECT * FROM REVERTS WHERE revert_id = ? ;
                """,
                (mem.id,),
            )
            row = cr.fetchone()
            print(row)
            notes = row[5]
            print(notes)
            #####################
            
            ## google sheet 
            try :
                cr.execute("SELECT * FROM REVERTS WHERE revert_id=?", (mem.id,))
                print (mem.id)
                row = cr.fetchone()
                cols = [str(row[1]),mem.name,row[2],row[6],ctx.author.name,row[4],row[5],row[7]]

                sheet.append_row(cols)
            
            except Exception as e:
                print(f"Google Sheets API Error: {e}")

            ###############################    
            cr.execute(
                        f"""
                                    INSERT INTO HISTORY (revert_id, state, mod_id, notes, date) VALUES (?, ?, ?, ?, datetime('now'));
                                """,
                                (row[1],row[6],row[3], row[5]),
                            )   

            connection.commit()            
    
 

    @commands.command()
    async def setmod(self, ctx :commands.Context, mod:discord.Member, *, mem: discord.Member | discord.User):

        cr.execute("""
            UPDATE REVERTS
            SET mod_id = ?
            WHERE id = (
                SELECT id
                FROM REVERTS
                WHERE revert_id = ?
            )
        """, (mod.id, mem.id))
        connection.commit()

        cr.execute("""
            UPDATE HISTORY
            SET mod_id = ?
            WHERE id = (
                SELECT id 
                FROM HISTORY
                WHERE revert_id = ?
                ORDER BY date DESC
                LIMIT 1
            )
        """, (mod.id, mem.id))
        connection.commit()
        cr.execute("""
            SELECT  * FROM REVERTS WHERE revert_id =? 
        """,(mem.id,))
        row = cr.fetchone()
        print("done")
        await ctx.send("DONE ✅")

        # try:
        #     if row :
        #         cell = sheet.find(str(mem.id))
        #         col_mod_name = cell.col+4

        #         #sheet.update(cell.row, col_mod_name, mod.name )
        #         worksheet.update_cell(cell.row, col_mod_name, mod.name)

        #     else:
        #         print("Row not found for mem.id:", mem.id)

        # except gspread.exceptions.APIError as e:
        #     print(f"Google Sheets API Error: {e}")

        # except sqlite3.Error as e:
        #     print(f"SQLite Error: {e}")

    @commands.command ()
    async def modcheck (self, ctx : commands.Context, *, mem: discord.Member ):
        print (mem)
        if not mem: 
            cr.execute("SELECT revert_id FROM REVERTS WHERE mod_id = ?;", (ctx.author.id,))
            reverts_ids = cr.fetchall()
            counter = 1

            embed = discord.Embed(title=f"Reverts assigned to you : ")
            embed.colour = discord.Colour.from_rgb(252, 186, 173)
            for row in reverts_ids:
                print(row)
                revert_id = row[0]
                embed.add_field(name=str(counter)+".", value=f"<@{revert_id}> ",inline=False)
                counter = counter+1 
            await ctx.send(embed=embed)
        else :
            cr.execute("SELECT revert_id FROM REVERTS WHERE mod_id = ?;", (mem.id,))
            reverts_ids = cr.fetchall()
            counter = 1

            embed = discord.Embed(title=f"Reverts assigned to {mem.name} : ")
            embed.colour = discord.Colour.from_rgb(69, 255, 202)
            for row in reverts_ids:
                print(row)
                revert_id = row[0]
                user = await ctx.bot.fetch_user(revert_id)

                if user:
                    username = user.display_name  # Use display_name to get the user's nickname if available
                else:
                    # If the user is not in the cache, you can use the user's ID as the username
                    username = f"User ID: {revert_id}"

                embed.add_field(name=str(counter) + "." +" "+ username, value=f"<@{revert_id}>", inline=False)
                counter += 1

            await ctx.send(embed=embed)



    @commands.command()
    async def info(self, ctx: commands.Context, mem: discord.Member | discord.User):
        cr.execute("SELECT * FROM REVERTS WHERE revert_id = ?;", (mem.id,))
        row = cr.fetchone()

        fmt_date = discord.utils.format_dt(datetime.fromisoformat(row[4]), style="D")

        if row:
            embed = discord.Embed(title="User Information: ", color=discord.Color.blue())
            embed.add_field(name="User : ", value=f"<@{row[1]}>", inline=True)
            embed.add_field(name="Gender: ", value=row[2], inline=False)
            embed.add_field(name="State: ", value=row[6], inline=False)
            embed.add_field(name="Main mod in contact: ", value=f"<@{row[3]}>", inline=True)
            embed.add_field(name="Date of last follow up: ", value=fmt_date, inline=False)
            embed.add_field(name="Follow-up notes: ", value=row[5], inline=False)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="the user is not found! ", color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command()
    async def history(self, ctx: commands.Context, mem: discord.Member | discord.User):
        cr.execute("SELECT mod_id, date, notes FROM HISTORY WHERE revert_id = ?", (mem.id,))

        rows = cr.fetchall()

        embed = discord.Embed(title=f"History for")
        embed.colour = discord.Colour.from_rgb(255, 255, 255)
        embed.description = f"<@{mem.id}>"
        for row in rows:
            mod_id, date, notes = row
            date = discord.utils.format_dt(datetime.fromisoformat(date), style="D")
            embed.add_field(name="Mod", value=f"<@{mod_id}> at {date}")
            embed.add_field(name="Note", value=notes, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def sheet(self,ctx):
        url_button = discord.ui.Button(
            label = "Click me", 
            url = "https://docs.google.com/spreadsheets/d/1P1OUWdwn-S7Q9BQhpnWpzPSPs8Amix6cCZAvyj055jo/edit?usp=sharing"
        )
        view = discord.ui.View()
        view.add_item(url_button)
        await ctx.send("Click the button to open the Google sheet:", view=view)

    @commands.command()
    async def timer(self,ctx : commands.Context , minutes: int, *, activity = None ) -> None:

        activitycr.execute("""
            INSERT INTO activity (mod_id, activity , time ,day) VALUES (?, ?, ?, ? );
        """, (ctx.author.id , activity , minutes, date.today() ))

        activity_conn.commit()

        duration_seconds = minutes * 60 

        embed = discord.Embed(
            title="Countdown Timer",
            description= f"{(floor(duration_seconds/60))} minutes {(floor(duration_seconds%60))} seconds remaining",
            color=0x00ff00  
        )

        
        timer_message = await ctx.send(embed=embed)
        user_mention = f'<@{ctx.author.id}>'

        for i in range(duration_seconds - 10, 0, -10):
            await asyncio.sleep(10)
            embed.description = f"{(floor(i/60))} minutes {(floor(i%60))} seconds remaining"
            await timer_message.edit(embed=embed)

        embed.colour = discord.Colour.from_rgb(199, 0, 57)
        embed.description = "Timer has ended!"
        await timer_message.edit(embed=embed)
        await ctx.send (user_mention)


        if ctx.author.id == 904066359426682900 :
            gif_url = 'https://tenor.com/view/cat-annoyed-cat-symm-annoyed-cat-gif-2854085661560673382'
            sendGIF= await ctx.send (gif_url)
            await asyncio.sleep(180)
            await sendGIF.delete()
            


# @bot.event
# async def on_raw_member_remove(payload):
    
#     member_id = payload.user_id

#     # You can fetch more information about the guild and member if needed
#     guild = bot.get_guild(guild_id)
#     member = await guild.fetch_member(member_id)
#     cr.execute(
#             f"""  
#             SELECT * FROM REVERTS WHERE revert_id = ? ;
#             """,
#             (member_id,),
#         )
#     row = cr.fetchone()
    
#     if row is not None:
#             embed = discord.Embed(description= f"**{member} HAS LEFT THE SERVER ! **", color=discord.Color.red())
#             await ctx.send(embed=embed)

# @bot.command(name="graphs")
# async def graphs(ctx: commands.Context):
#     cr.execute("SELECT gender, count(gender) FROM REVERTS GROUP BY gender;")
#     rows = cr.fetchall()
#     genders = [item[0] for item in rows]
#     counts = [item[1] for item in rows]
#     colors = ["#F79BD3", "#91C8E4"]
#     plt.pie(counts, labels=genders, autopct="%1.1f%%", startangle=140, colors=colors)
#     plt.axis("equal")
#     plt.title("Reverts statistics")
#     plt.savefig("plot.png")
#     embed = discord.Embed(
#         title="Graph Embed", description="This is a graph generated by the bot.", color=discord.Color.blue()
#     )
#     file = discord.File("plot.png", filename="plot.png")
#     embed.set_image(url="attachment://plot.png")
#     await ctx.send(embed=embed, file=file)



