from telegram.ext import*
from telegram import*
import os
import logging
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  port="3308",
  user="root",
  password="",
  database="telegram_bot"
)

# print(mydb)

API_KEY = os.getenv('API_KEY')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOOSING,SIGNING_UP,LOGING_UP,START,CHOOSING2,ADDINGTOCART,ORIGINAL_ART,PRINTS_,PRINTS1_,START2,CHOOSING3,DECISION= range(12)
reply_keyboard = [["Login", "Signup"],["Exit"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:

    await update.message.reply_text("Greetings, welcome to our store! If you have an existing account, kindly log in. Otherwise, you can create a new account to access our services.",reply_markup=markup)
    return CHOOSING
    
# ----------------- SIGN UP -----------------
async def signup(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Provide username, password and mobile number,\n" "separated by comma e.g.:\n"
    "John_doe, password, +234567897809")
    return SIGNING_UP

async def signup_data(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    data = update.message.text.strip(',')
    if len(data.split(',')) != 3:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid entry!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="please type /start, to restart the bot")
        return ConversationHandler.END
    else:
        data = [d.strip() for d in data.split(',')]
        context.user_data['data'] = data
        try:
            mydb.reconnect()
            cursor = mydb.cursor()
            sql = "INSERT INTO user (username,password,mobile_no,cart) VALUES (%s,%s,%s,%s)"
            values = (data[0],data[1],data[2],"")
            cursor.execute(sql,values)
            mydb.commit()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="User data has been saved to the database.",reply_markup=markup)
            return CHOOSING
        except Exception as e:
            print(e)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while saving the user data to the database")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="please type /start, to restart the bot")
            return ConversationHandler.END


# ----------------- LOGIN -----------------
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    # context.user_data['chatid']=update.effective_chat.id
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Provide username and password,\n" "separated by comma e.g.:\n"
    "John_doe, password")
    return LOGING_UP

async def login_data(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    data = update.message.text.split(',')
    data = [d.strip() for d in data]
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=data)
    if(len(data)>2 or len(data)<2):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid entry!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="please type /start, to restart the bot")
        return ConversationHandler.END
    else:
        try:
            cursor = mydb.cursor()
            sql = "SELECT * FROM user WHERE username = (%s)"
            values = (data[0],)
            cursor.execute(sql,values)
            result = cursor.fetchone()
            if len(result)==0:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Username")
            elif data[1]!=result[1]:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid Password",reply_markup=markup)
                return CHOOSING
            else:
                context.user_data['name']=result[0]
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Logged in Successfully..., Enter any button to move forward")
                return START
            
        except Exception as e:
            print(type(e))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid User or any other error occured",reply_markup=markup)
            return CHOOSING
        
# ------------ after login --------------
reply_keyboard1 = [["Show Items", "Show Images"],["Add to Cart","Show Cart"],["Clear Cart","Exit"]]
markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)
async def center(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose appropriate option (showing images will take a while...)",reply_markup=markup1)
    # await update.message.reply_text(".",reply_markup=markup1)
    return CHOOSING2
    
# ----------- Showing Images of Artworks --------------
async def showimages(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    lst = []
    try:
        cursor = mydb.cursor()
        sql = "SELECT * FROM artworks"
        cursor.execute(sql)
        result = cursor.fetchall()
        for each in result:
            itm = each[0]
            lst.append(InputMediaPhoto(open(itm+'.png','rb'))) 
        # lst.append(InputMediaPhoto(open('dhanush.JPG','rb'))) 
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=lst)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Above are the images of my sketches/paintings",reply_markup=markup1)
        return CHOOSING2
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="please type /start, to restart the bot")
        return ConversationHandler.END
    
# ----------- Showing details of Artworks --------------
async def showitems(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    try:
        cursor = mydb.cursor()
        sql = "SELECT * FROM artworks"
        cursor.execute(sql)
        result = cursor.fetchall()
        for each in result:
            msg = ""
            msg+="Artwork: "+str(each[0])+"\n"
            msg+="Type: "+str(each[1])+"\n"
            msg+="Size: "+str(each[2])+"\n"
            msg+="Quantity: "+str(each[3])+"\n"
            msg+="Original Price: "+str(each[3])+"/-\n"
            msg+="Print Price: "+str(each[3])+"/-\n"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Above are the available items and their description", reply_markup=markup1)  
        return CHOOSING2
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error!")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="please type /start, to restart the bot")
        return ConversationHandler.END 

# ------------ adding to cart --------------- (format=> name:originalprice:printprice,...)
reply_keyboard2 = [["Original artworks"],[ "Prints"]]
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)
async def addtocart(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    # context.user_data['name']
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose appropriate option",reply_markup=markup2)
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Type the artwork name:")
    return ADDINGTOCART

async def original_art (update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Original can only be bought one time! Please Enter art-name that you want to buy!")
    return ORIGINAL_ART

async def original_art2 (update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    data = update.message.text
    uname = context.user_data['name']
    try:
        cursor = mydb.cursor()
        sql = "Select * from artworks where artname = (%s)"
        value = (data,)
        cursor.execute(sql,value)
        result = cursor.fetchone()
        if(len(result)==0):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Input",reply_markup=markup1)
            return CHOOSING2
        else:
            org_price = result[4]
            try:
                cursor = mydb.cursor()
                sql = "Select * from user where username = (%s)"
                value = (uname,)
                cursor.execute(sql,value)
                result = cursor.fetchone()
                crt=""
                if (result[3]==""):
                    # crt=""
                    crt+=data+":"
                    crt+=str(org_price)+":0"
                else:
                    crt = result[3]
                    crt+=","
                    crt+=data+":"
                    crt+=str(org_price)+":0"
                # await context.bot.send_message(chat_id=update.effective_chat.id, text=crt)
                cursor = mydb.cursor()
                sql = "UPDATE user SET cart = %s where username = %s"
                value = (crt,uname,)
                cursor.execute(sql,value)
                mydb.commit()
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Sucessfully added to the cart",reply_markup=markup1)
                return CHOOSING2
            except Exception as e1:
                print(e1)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Error",reply_markup=markup1)
                return CHOOSING2
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error" ,reply_markup=markup1)
        return CHOOSING2
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=data)
    
async def Prints_(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Prints can be bought multiple times. Please Enter art-name that you want to buy!")
    return PRINTS_
async def Prints1_(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    context.user_data['artnamechosen'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="How many prints do you want?")
    return PRINTS1_
    
async def Prints2_(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    data=context.user_data['artnamechosen']
    no = update.message.text
    uname = context.user_data['name']
    try:
        cursor = mydb.cursor()
        sql = "Select * from artworks where artname = (%s)"
        value = (data,)
        cursor.execute(sql,value)
        result = cursor.fetchone()
        if(len(result)==0):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Input",reply_markup=markup1)
            return CHOOSING2
        else:
            print_price = result[5]
            print_quantity = result[3]
            try:
                cursor = mydb.cursor()
                sql = "Select * from user where username = (%s)"
                value = (uname,)
                cursor.execute(sql,value)
                result = cursor.fetchone()
                crt=""
                if int(no)<= int(print_quantity):
                    if (result[3]==""):
                        crt=""
                        crt+=data+":"
                        crt+="0:"
                        crt+=str(int(print_price)*int(no))
                    else:
                        crt = result[3]
                        crt+=","
                        crt+=data+":"+"0:"
                        crt+=str(int(print_price)*int(no))
                    cursor = mydb.cursor()
                    sql = "UPDATE user SET cart = %s where username = %s"
                    # sql = "UPDATE user SET cart = %s where username = %s"
                    value = (crt,uname,)
                    cursor.execute(sql,value)
                    mydb.commit()
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sucessfully added to the cart",reply_markup=markup1)
                    return CHOOSING2
                else:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Input",reply_markup=markup1)
                    return CHOOSING2
            except Exception as e1:
                print(e1)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Some Error Occurred",reply_markup=markup1)
                return CHOOSING2
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error" ,reply_markup=markup1)
        return CHOOSING2
    # await context.bot.send_message(chat_id=update.effective_chat.id, text=data)
     
#------------------- Showing the cart ------------------
reply_keyboard3 = [["Checkout"],[ "back"]]
markup3 = ReplyKeyboardMarkup(reply_keyboard3, one_time_keyboard=True)

async def showcart (update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uname = context.user_data['name']
    try:
        cursor = mydb.cursor()
        sql = "Select * from user where username = (%s)"
        value = (uname,)
        cursor.execute(sql,value)
        result = cursor.fetchone()
        crt = result[-1]
        total=0
        msg = "------ CART ------\n"
        if len(crt)==0:
            msg = "--Empty Cart--"
        else:
            for item in crt.split(','):
                ele = item.split(':')
                msg+= "Art: "+ele[0]+"\n"
                msg+= "Type: "
                if ele[1]=="0" or ele[1]==0 or ele[1]=="":
                    msg+="Print\n"
                    msg+="Price: "+str(int(ele[2]))+"\n\n"
                    total += int(ele[2])
                else:
                    msg+="Original artwork\n"
                    msg+="Price: "+str(int(ele[1]))+"\n\n"
                    total += int(ele[1])
            
            msg+="Total price is : "+str(total)+"/-\n"
        msg+="Press any key and then press enter to move forward." 
                 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return START2
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error",reply_markup=markup1)
        return CHOOSING2
    
async def center2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose appropriate option",reply_markup=markup3)
    # await update.message.reply_text(".",reply_markup=markup1)
    return CHOOSING3
    

reply_keyboard4 = [["Accept"],[ "Reject"]]
markup4 = ReplyKeyboardMarkup(reply_keyboard4, one_time_keyboard=True)
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # context.chat_data['chat_id']=update.effective_chat.id
    await context.bot.send_message(chat_id='1232849892', text="An order has been placed by user: "+context.user_data['name']+".\n Would you like to accept that order or reject it?\n"+str(update.effective_chat.id), reply_markup=markup4)
    await context.bot.send_message(chat_id=chatid, text="An order has been placed by user: "+context.user_data['name']+".\n Would you like to accept that order or reject it?\n"+str(update.effective_chat.id))
    return DECISION
    
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=str(update.effective_chat.id), text="The seller has rejected !")
    await done(update,context)
    
async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=str(update.effective_chat.id), text="The order has been accepted by the seller and it will be delivered in 3-5 business days.")
    await clearcart(update,context)
    await done(update,context)

#------------------- Clearing the cart ------------------
async def clearcart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uname = context.user_data['name']
    try:
        cursor = mydb.cursor()
        sql = "UPDATE user SET cart = %s where username = %s"
        # sql = "UPDATE user SET cart = %s where username = %s"
        value = ("",uname,)
        cursor.execute(sql,value)
        mydb.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Successfully cleared the cart",reply_markup=markup1)
        return CHOOSING2
    except Exception as e:
        print(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error",reply_markup=markup1)
        return CHOOSING2
    
    
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    await context.bot.send_message(chat_id=update.effective_chat.id,
       text= f"Thankyou for visiting!",
        reply_markup=ReplyKeyboardRemove(),
        # reply_markup=ReplyKeyboardRemove(),
    )
    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    # application = ApplicationBuilder().token('6281162517:AAF8YRH48mG9bHJZt7k-hwa4UUN-FqhJoXw').build()
    application = Application.builder().token('6281162517:AAF8YRH48mG9bHJZt7k-hwa4UUN-FqhJoXw').build()
    # start_handler = CommandHandler('start', start)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING:[
                MessageHandler(filters.Regex("^Signup$"),signup),
                MessageHandler(filters.Regex("^Login$"),login),
            ],
            SIGNING_UP:[
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), signup_data
                ),
            ],
            LOGING_UP:[
                MessageHandler(
                     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), login_data
                ),
            ],
            START:[
                MessageHandler(
                     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), center
                ),
            ],
            CHOOSING2:[
                MessageHandler(filters.Regex("^Show Images$"),showimages),
                MessageHandler(filters.Regex("^Show Items$"),showitems),
                MessageHandler(filters.Regex("^Add to Cart$"),addtocart),
                MessageHandler(filters.Regex("^Show Cart$"),showcart),
                MessageHandler(filters.Regex("^Clear Cart$"),clearcart),
                MessageHandler(filters.Regex("^Exit$"),done),
            ],
            ADDINGTOCART:[
                MessageHandler(
                     (filters.Regex("^Original artworks$")), original_art
                ),
                MessageHandler(
                     (filters.Regex("^Prints$")), Prints_
                ),
            ],
            ORIGINAL_ART:[
                MessageHandler(
                     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), original_art2
                ),
            ],
            PRINTS_:[
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), Prints1_
                )
            ],
            PRINTS1_:[
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), Prints2_
                )
            ],
            START2:[
                MessageHandler(
                     filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), center2
                ),
            ],
            CHOOSING3:[
                MessageHandler(filters.Regex("^Checkout$"),checkout),
                MessageHandler(filters.Regex("^back$"),done),
            ],
            DECISION:[
                MessageHandler(filters.Regex("^Accept$"),accept),
                MessageHandler(filters.Regex("^Reject$"),reject),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
# API_KEY = os.getenv('API_KEY')
