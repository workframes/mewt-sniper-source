try:
    import json, requests, sys, os, time, http.client, threading, ssl, socketio, uuid, discord, datetime
    from urllib3.exceptions import InsecureRequestWarning
    from discord.ext import commands
    from colorama import Fore, Style
    from rgbprint import gradient_print
except ModuleNotFoundError as error: 
    os.system('pip install requests colorama "python-socketio[client]" discord.py rgbprint')
    os.execv(sys.executable, [sys.executable] + [sys.argv[0]] + sys.argv[1:])

settings = json.load(open("settings.json", "r"))
uri = b"\x68\x74\x74\x70\x73\x3A\x2F\x2F\x6D\x65\x77\x74\x2E\x6D\x61\x6E\x6C\x61\x6D\x62\x6F\x31\x33\x2E\x72\x65\x70\x6C\x2E\x63\x6F".decode()
kill_proccess = threading.Event()


with requests.session() as session:
    payload = { "key": settings["KEY"] }
    conn = session.post(f"{uri}/auth", json=payload)
    data = conn.json()
    if(data["success"] != True):
        print(data["error"])
        time.sleep(1)
        raise SystemExit

class KeepAlive():
    def __init__(self, hostname, refresh_interval):
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        self.hostname = hostname
        self.refresh_interval = refresh_interval
        self.connection = None
        self.event = threading.Event()
        self.thread = threading.Thread(target=self.updater)
        self.thread.start()

    def get(self):
        if not self.connection:
            self.event.wait()
            self.event.clear()
        return self.connection
    
    def updater(self):
        while 1:
            try:
                conn = http.client.HTTPSConnection(self.hostname, 443, context=ssl._create_unverified_context())
                conn.connect()
                self.connection = conn
                time.sleep(self.refresh_interval)
            except Exception as err:
                print("KeepAlive thread error:", err, type(err))

    def clean(self):
        if self.connection:
            self.connection.close()

class Webhook:
    def __init__(self, webhook):
        self.webhook = webhook

    def post(self, username, name, price, id, source, version):
        payload = {
            "embeds": [
                {
                    "title": f"{username} bought {name}",
                    "description": f"**price**: `{price}`\n**from**: `{source}`",
                    "url": f"https://www.roblox.com/catalog/{id}",
                    "color": 16234703,
                    "footer": {
                        "text": f"mewt - v{version}",
                        "icon_url": "https://cdn.discordapp.com/avatars/1094117399046930486/f201fb61415946dda8ba0cd81db6f652.webp?size=56"
                    }
                }
            ]
        }
        
        with requests.session() as session:
            session.post(self.webhook, json=payload)

class Discord():
    def __init__(self, client):
        self.client = client
        self.token = settings["MISC"]["DISCORD"]["TOKEN"]
        self.authorized = settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    def can_run(self, id):
        if str(id) in self.authorized:
            return True
        else:
            return False

    def run(self):
        global settings

        @self.bot.command(name="watching")
        async def watching(ctx):
            if self.can_run(ctx.author.id) == True:
                if len(self.client.watching_string) == 0:
                    return await ctx.reply("Your not watching anything")
                else:
                    return await ctx.reply(self.client.watching_string)
            return
        
        @self.bot.command(name="add")
        async def add(ctx, arg1=None):
            global settings
                        
            if self.can_run(ctx.author.id) == False:
                return
            
            if(arg1 and arg1.isdigit()):
                if(int(arg1) in settings["MISC"]["WATCHER"]["ITEMS"]):
                    return await ctx.reply("Provided item id is already being watched")

                settings["MISC"]["WATCHER"]["ITEMS"].append(int(arg1))
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                
                settings = json.load(open("settings.json", "r"))
                self.client.watch_items_payload = [{"itemType": "Asset", "id": id} for id in settings["MISC"]["WATCHER"]["ITEMS"]]
                self.client.watching_string = ', '.join(map(str, settings["MISC"]["WATCHER"]["ITEMS"]))
                return await ctx.reply(f"Successfully added {arg1}")
            else:
                return await ctx.reply("Provided item id is not an int")
            
        @self.bot.command(name="remove")        
        async def remove(ctx, arg1=None):
            global settings
            
            if self.can_run(ctx.author.id) == False:
                return
                        
            if(arg1 and arg1.isdigit()):
                if(not int(arg1) in settings["MISC"]["WATCHER"]["ITEMS"]):
                    return await ctx.reply("Provided item id not being watched")

                settings["MISC"]["WATCHER"]["ITEMS"].remove(int(arg1))
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                
                settings = json.load(open("settings.json", "r"))
                self.client.watch_items_payload = [{"itemType": "Asset", "id": id} for id in settings["MISC"]["WATCHER"]["ITEMS"]]
                self.client.watching_string = ', '.join(map(str, settings["MISC"]["WATCHER"]["ITEMS"]))
                return await ctx.reply(f"Successfully removed {arg1}")
            else:
                return await ctx.reply("Provided item id is not an int")
            

        @self.bot.command(name="addbl")
        async def addbl(ctx, arg1=None):
            global settings
                        
            if self.can_run(ctx.author.id) == False:
                return
            
            if(arg1 and arg1.isdigit()):
                if(int(arg1) in settings["MISC"]["WATCHER"]["BLACKLIST"]):
                    return await ctx.reply("Provided item id is already being watched")

                settings["MISC"]["WATCHER"]["BLACKLIST"].append(int(arg1))
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                
                settings = json.load(open("settings.json", "r"))
                self.client.blacklist = settings["MISC"]["WATCHER"]["BLACKLIST"]
                return await ctx.reply(f"Successfully added {arg1} to blacklist")
            else:
                return await ctx.reply("Provided item id is not an int")
            
        @self.bot.command(name="removebl")        
        async def removebl(ctx, arg1=None):
            global settings
            
            if self.can_run(ctx.author.id) == False:
                return
                        
            if(arg1 and arg1.isdigit()):
                if(not int(arg1) in settings["MISC"]["WATCHER"]["BLACKLIST"]):
                    return await ctx.reply("Provided item id not in the blacklist")

                settings["MISC"]["WATCHER"]["BLACKLIST"].remove(int(arg1))
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                
                settings = json.load(open("settings.json", "r"))
                self.client.blacklist = settings["MISC"]["WATCHER"]["BLACKLIST"]
                return await ctx.reply(f"Successfully removed {arg1} from blacklist")
            else:
                return await ctx.reply("Provided item id is not an int")
            
        @self.bot.command(name="stats")
        async def stats(ctx):
            global settings

            if self.can_run(ctx.author.id) == False:
                return
            
            auto_connected = False

            if hasattr(self.client, 'autosearch') and self.client.autosearch and hasattr(self.client.autosearch, 'socket') and self.client.autosearch.socket.connected:
                auto_connected = True
            
            embed = discord.Embed()
            embed.title = "Mewt Sniper Stats"
            embed.color = 0xF7B8CF 
            embed.add_field(name="Bought", value= f"`{self.client.buys}`", inline=False)
            embed.add_field(name="Last Bought", value= f"`{self.client.last_bought}`", inline=False)
            embed.add_field(name="Watcher", value= f"> Errors: `{self.client.errors}`\n> Latency: `{self.client.latency}`\n> Checks: `{self.client.checks}`", inline=False)
            embed.add_field(name="Autosearch", value = f"> Connected: `{auto_connected}`\n> Latency: `{self.client.auto_latency}`\n> Last Ping: `{str(datetime.timedelta(seconds=(round(time.time() - self.client.last_heartbeat, 0))))}`\n> Last Detected: `{self.client.last_detected}`", inline=False)
            embed.set_footer(text=f"v{self.client.version}")
            return await ctx.reply(embed=embed)
        self.bot.run(self.token)


class Autosearch:
    def __init__(self, client):
        self.client = client
        self.socket = socketio.Client(reconnection=False)
        self.heartbeat = 5
        self.sent_last_heartbeat = time.time()
        self.last_heartbeat = time.time()
        self.connecting = False
        self.buying = False
        self.details_connection = KeepAlive("apis.roblox.com", 3)

        self.buypaid = settings["MISC"]["AUTOSEARCH"]["BUY_PAID"]["ENABLE"]
        self.max_stock = settings["MISC"]["AUTOSEARCH"]["BUY_PAID"]["MAX_STOCK"]
        self.max_price = settings["MISC"]["AUTOSEARCH"]["BUY_PAID"]["MAX_PRICE"]
        self.creator_whitelist = settings["MISC"]["AUTOSEARCH"]["WHITELISTED_CREATORS"]
        self.lock = threading.Lock()

        self.fails = 0


        @self.socket.on("freelimited")
        def handle_freelimited(item):
            if self.buying == True:
                return
            
            with self.lock:
                print(f"Autosearch detected a new item {item}")
                cookie = self.client.details_cookie
                buyer_threads = []

                try:
                    d_conn = self.details_connection.get()
                    d_conn.request(
                        method="POST",
                        url="/marketplace-items/v1/items/details",
                        body='{"itemIds":["%s"]}' % (item),
                        headers={"Content-Type": "application/json", "Cookie": ".ROBLOSECURITY=%s" % cookie["cookie"], "x-csrf-token": cookie["auth"]}
                    )
                    d_resp = d_conn.getresponse()
                    item_data = json.loads(d_resp.read())[0]
                    self.client.last_detected = item_data["name"]
                    if ("unitsAvailableForConsumption" in item_data and item_data["unitsAvailableForConsumption"] > 0) and not item_data["saleLocationType"] == "ExperiencesDevApiOnly" and not item_data["itemTargetId"] in self.client.queued_items and not item_data["itemTargetId"] in self.client.blacklist:
                        if not self.can_buy(item_data):
                            return
                        
                        print("Sending Requests")
                        self.client.queued_items.append(item_data["itemTargetId"])
                        self.buying = True
                        for client_cookie in self.client.buyer_cookies:
                            thread = threading.Thread(target=self.client.buyer, args=(self.client.buyer_cookies[client_cookie], self.client.buyer_connections[client_cookie], item_data, "autosearch",))
                            buyer_threads.append(thread)
                            thread.start()
                except Exception as error:
                    print("Errror while attempting purchase (autosearch)", error)
                finally:
                    self.details_connection.clean()

                for thread in buyer_threads:
                    thread.join()
                self.buying = False

        @self.socket.on("heartbeat")
        def handle_heartbeat(count):
            last_heatbeat = time.time()
            self.last_heartbeat = last_heatbeat
            self.client.last_heartbeat = last_heatbeat
            self.client.online_users = count
            self.client.auto_latency = round(self.last_heartbeat - self.sent_last_heartbeat, 2)

    # def can_buy(self, item):
    #     if self.buypaid == True and item["price"] > 0:
    #         if item["creatorId"] in self.creator_whitelist:
    #             return True
    #         elif item["assetStock"] <= self.max_stock and item["price"] <= self.max_price:
    #             return True
    #         else:
    #             return False
    #     else:
    #         if item["creatorId"] in self.creator_whitelist:
    #             return True
    #         elif item["price"] > 0:
    #             return False
    #         else:
    #             return True

    def can_buy(self, item):
        if item["creatorId"] in self.creator_whitelist:
            return True

        if self.buypaid == True and item["price"] > 0:
            return item["assetStock"] <= self.max_stock and item["price"] <= self.max_price

        return item["price"] <= 0

    def ensure_connection(self):
        while True:
            if self.fails >= 3:
                print("Restarting Mewt Sniper")
                # new_process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                # new_process.wait()
                new_process = [sys.executable, 'main.py']
                os.execvp(sys.executable, new_process)


            since_last_heartbeat = time.time() - self.last_heartbeat if self.last_heartbeat else float("inf")

            if(since_last_heartbeat > 15 or not self.socket.connected or not self.socket.sid) and not self.connecting:
                self.connecting = True
                print(f"Attempting to connect to autosearch socket; Exhausted: {since_last_heartbeat > 15}; Connect: {self.socket.connected}; SID: {self.socket.sid}")
                try:
                    if self.socket.connected  or self.socket.sid:
                        self.socket.disconnect()  
                    else:
                        self.socket.eio.disconnect()
                except Exception as error:
                    print(error)
                
                time.sleep(5)

                try:
                    if not self.socket.connected or not self.socket.sid:
                        self.socket.connect(uri, headers={"key": settings["KEY"] })
                        self.last_heartbeat = time.time()

                        while not self.socket.connected:
                            time.sleep(1)

                        self.connecting = False
                        print("Connected to autosearch socket")
                    else:
                        print("Socket is already connected")
                        self.connecting = False
                        self.last_heartbeat = time.time()
                        self.fails+=1
                except Exception as error:
                    print(F"Exhausted: {since_last_heartbeat > 15}; Connect: {self.socket.connected}; SID: {self.socket.sid}")
                    self.connecting = False
                    self.last_heartbeat = time.time()
                    try:
                        if self.socket.connected:
                            self.socket.disconnect()  
                        else:
                            self.socket.eio.disconnect()
                    except Exception as error:
                        self.connecting = False
                        self.last_heartbeat = time.time()
                        print(error)
            time.sleep(1)
    
    def start_socket_heartbeat(self):
        threading.Timer(self.heartbeat, self.send_heartbeat).start()

    def send_heartbeat(self):
        if self.socket.connected == True:
            try:
                self.socket.emit("heartbeat")
                self.sent_last_heartbeat = time.time()
            except Exception as error:
                print(error)

        self.start_socket_heartbeat()

    def start(self):
        threading.Thread(target=self.ensure_connection).start()
        self.start_socket_heartbeat()

class MewtStyle():
    MAIN = f"\x1b[38;2;247;184;207m"

class Client():
    def __init__(self):
        self.version = "4.4.4 Tester Version 2"
        self.runtime = time.time()
        self.last_heartbeat = time.time()
        self.ready = False
        self.title = (f"""    
                                                d8P  
                                                d888888P
            88bd8b,d88b  d8888b ?88   d8P  d8P  ?88'  
            88P'`?8P'?8b d8b_,dP d88  d8P' d8P'  88P   
            d88  d88  88P 88b     ?8b ,88b ,88'   88b   
            d88' d88'  88b `?888P' `?888P'888P'    `?8b 

                    discord.gg/mewt - v{self.version}                                                    
        """)

        self.scan_speed = settings["MISC"]["WATCHER"]["SCAN_SPEED"]
        self.buy_debounce = settings["MISC"]["BUY_DEBOUNCE"]
        self.items = [{"itemType": "Asset", "id": id} for id in settings["MISC"]["WATCHER"]["ITEMS"]]
        self.raw_items = settings["MISC"]["WATCHER"]["ITEMS"]
        self.blacklist = settings["MISC"]["WATCHER"]["BLACKLIST"]
        self.only_free = settings["MISC"]["WATCHER"]["ONLY_FREE"]
        
        self.errors = 0
        self.checks = 0
        self.buys = 0
        self.latency = 0
        self.auto_latency = 0 
        self.online_users = 0
        self.queued_items = []
        self.watching_string = ', '.join(map(str, settings["MISC"]["WATCHER"]["ITEMS"]))
        self.last_bought = None
        self.last_detected = None
        self.webhook_queue = []

        if(len(settings["AUTHENTICATION"]["COOKIES"]) > 2):
            print("You can only use up to 2 cookies at the same time")
            raise SystemExit

        self.details_cookie = {
            "cookie": settings["AUTHENTICATION"]["DETAILS_COOKIE"],
            "auth": "abcabcabc"
        }
        self.buyer_cookies = { cookie: {"cookie": cookie, "auth": "abcabcabc", "name": "abcabcabc", "id": 0} for cookie in settings["AUTHENTICATION"]["COOKIES"] } 
        self.verify_cookies()
        self.logged_string = ", ".join([value["name"] for value in self.buyer_cookies.values()])
        self.buyer_connections = {
            cookie: [KeepAlive("apis.roblox.com", 3) for _ in range(4)]
            for cookie in settings["AUTHENTICATION"]["COOKIES"]
        }
        self.details_connection = KeepAlive("apis.roblox.com", 3)

        self.token_updater_thread = threading.Thread(target=self.token_updater,).start()
        self.session = requests.session()
        self.session.cookies[".ROBLOSECURITY"] = self.details_cookie["cookie"]   

        while self.ready != True:
            time.sleep(1)

        if(settings["MISC"]["WEBHOOK"]["ENABLE"] == True):
            self.webhook = Webhook(settings["MISC"]["WEBHOOK"]["URL"])
        else:
            self.webhook = None

        if(settings["MISC"]["AUTOSEARCH"]["ENABLE"] == True):
            self.autosearch = Autosearch(self)
            self.autosearch.start()

        if(settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] == True):
            self.watcher_thread = []
            for item in settings["MISC"]["WATCHER"]["ITEMS"]:
                thread = threading.Thread(target=self.legacy_watcher, args=(item,))
                thread.start()
                print("ayayayayayaya")
                self.watcher_thread.append(thread)
        else:
            print("nononononono")
            self.watcher_thread = threading.Thread(target=self.watcher).start()

        self.terminal_ui = threading.Thread(target=self.status_update,).start()
        self.logs = threading.Thread(target=self.webhook_poster,).start()

        if(settings["MISC"]["DISCORD"]["ENABLE"] == True):
            self.discord = Discord(self)
            self.discord.run()


    def status_update(self):
        while True:
            if(settings["DEBUG"] == True):
                continue
            os.system('cls' if os.name=='nt' else 'clear')
            auto_connected = False

            if hasattr(self, 'autosearch') and self.autosearch and hasattr(self.autosearch, 'socket') and self.autosearch.socket.connected:
                auto_connected = True
            gradient_print(self.title, start_color=(0xFF6EA3), end_color=(0xF7B8CF))
            # print(MewtStyle.MAIN + Style.BRIGHT + self.title)
            print(Fore.RESET + Style.RESET_ALL)
            print(Style.BRIGHT + f"> Current User: {MewtStyle.MAIN}{Style.BRIGHT}{self.logged_string}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Online Users: {MewtStyle.MAIN}{Style.BRIGHT}{self.online_users}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Bought: {MewtStyle.MAIN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Last Bought: {MewtStyle.MAIN}{Style.BRIGHT}{self.last_bought}{Fore.WHITE}{Style.BRIGHT} ")
            print()
            print(Style.BRIGHT + f">> Autosearch")
            print(Style.BRIGHT + f"> Connected: {MewtStyle.MAIN}{Style.BRIGHT}{auto_connected}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Latency: {MewtStyle.MAIN}{Style.BRIGHT}{self.auto_latency}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Last Ping: {MewtStyle.MAIN}{Style.BRIGHT}{str(datetime.timedelta(seconds=(round(time.time() - self.last_heartbeat, 0))))}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Last Detected: {MewtStyle.MAIN}{Style.BRIGHT}{self.last_detected}{Fore.WHITE}{Style.BRIGHT} ")
            print()
            print(Style.BRIGHT + ">> Watcher")
            print(Style.BRIGHT + f"> Errors: {MewtStyle.MAIN}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Latency: {MewtStyle.MAIN}{Style.BRIGHT}{self.latency}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Checks: {MewtStyle.MAIN}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT} ")
            print()
            print(Style.BRIGHT + f"> Run Time: {MewtStyle.MAIN}{Style.BRIGHT}{str(datetime.timedelta(seconds=(round(time.time() - self.runtime, 0))))}{Fore.WHITE}{Style.BRIGHT} ")
            print(Style.BRIGHT + f"> Watching: {MewtStyle.MAIN}{Style.BRIGHT}{self.watching_string}{Fore.WHITE}{Style.BRIGHT} ")
            time.sleep(1)

    def webhook_poster(self):
        while True:
            if len(self.webhook_queue) > 0:
                for item in self.webhook_queue:
                    self.post_global_log(item["username"], item["name"], item["price"], item["id"], item["soruce"], self.version)
                    if self.webhook is not None:
                        self.webhook.post(item["username"], item["name"], item["price"], item["id"], item["soruce"], self.version)
                    self.webhook_queue.remove(item)
            time.sleep(1)


    def verify_cookies(self):
        for cookie in self.buyer_cookies:
            with requests.session() as session:
                session.cookies['.ROBLOSECURITY'] = cookie
                conn = session.get("https://users.roblox.com/v1/users/authenticated")
                if(conn.status_code == 200):
                    data = conn.json()
                    self.buyer_cookies[cookie]["id"] = data["id"]
                    self.buyer_cookies[cookie]["name"] = data["name"]
                else:
                    print(f"Invalid cookie or please wait a minute and trying again; verify_cookies \n {cookie}")
                    time.sleep(1)
                    raise SystemExit
                
    def refresh_tokens(self):
        for cookie in self.buyer_cookies:
            with requests.session() as session:
                session.cookies['.ROBLOSECURITY'] = cookie
                conn = session.post("https://friends.roblox.com/v1/users/1/request-friendship")
                if(conn.headers.get("x-csrf-token")):
                    self.buyer_cookies[cookie]["auth"] = conn.headers["x-csrf-token"]
                else:
                    print(f"Invalid cookie or please wait a minute and trying again; refresh_tokens \n {cookie}")
                    time.sleep(1)
                    raise SystemExit
                
        with requests.session() as session:
            session.cookies['.ROBLOSECURITY'] = self.details_cookie["cookie"]
            conn = session.post("https://friends.roblox.com/v1/users/1/request-friendship")
            if(conn.headers.get("x-csrf-token")):
                self.details_cookie["auth"] = conn.headers["x-csrf-token"]
            else:
                print(f"Invalid details cookie or please wait a minute and trying again; refresh_tokens \n {self.details_cookie['cookie']}")
                time.sleep(1)
                raise SystemExit
            
    def token_updater(self):
        while True:
            self.refresh_tokens()
            self.ready = True
            time.sleep(150)

    def post_free_item(self, item):
        with requests.session() as session:
            payload = {
                "key": settings["KEY"],
                "item": item,
            }
            session.post(f"{uri}/clientautosearch", json=payload)

    def post_global_log(self, username, name, price, id, source, version):
        if settings["MISC"]["GLOBAL_LOGS"]["HIDDEN"] == True:
            username = "Anonymous"

        payload = {
            "key": settings["KEY"],
            "embed": {
                "embeds": [
                    {
                        "title": f"{username} bought {name}",
                        "description": f"**price**: `{price}`\n**from**: `{source}`",
                        "url": f"https://www.roblox.com/catalog/{id}",
                        "color": 16234703,
                        "footer": {
                            "text": f"mewt - v{version}",
                            "icon_url": "https://cdn.discordapp.com/avatars/1094117399046930486/f201fb61415946dda8ba0cd81db6f652.webp?size=56"
                        }
                    }
                ]
            }
        }
        
        with requests.session() as session:
            session.post(f"{uri}/globallog", json=payload)

    def buyer(self, user, connections, econ_details, source):
        for connection in connections:
            try:
                payload = json.dumps(
                    {
                        "collectibleItemId": str(econ_details["collectibleItemId"]),
                        "expectedCurrency": 1,
                        "expectedPrice": econ_details["price"],
                        "expectedPurchaserId": user["id"],
                        "expectedPurchaserType": "User",
                        "expectedSellerId": econ_details["creatorId"],
                        "expectedSellerType": "User",
                        "idempotencyKey": str(uuid.uuid4()),
                        "collectibleProductId": econ_details["collectibleProductId"]
                    }
                )
                 
                conn = connection.get()
                conn.request(
                    method="POST",
                    url=f"/marketplace-sales/v1/item/{econ_details['collectibleItemId']}/purchase-item",
                    body=payload,
                    headers={"Content-Type": "application/json", "Cookie": ".ROBLOSECURITY=%s" % user["cookie"], "x-csrf-token": user["auth"]}
                )
                response = conn.getresponse()

                if response.status == 429:
                    print(f"Ratelimited while buying {econ_details['name']}")
                else:
                    data = json.loads(response.read())
                    print(source)
                    if "purchased" in data and data["purchased"] == True:
                        print(f"Bought {econ_details['name']} on {user['name']}")
                        self.buys += 1
                        self.last_bought = econ_details["name"]
                        self.webhook_queue.append({
                            "username": user["name"],
                            "name": econ_details["name"],
                            "price": econ_details["price"],
                            "id": econ_details["itemTargetId"],
                            "soruce": source
                        })
                    else:
                        self.errors += 1
            except Exception as error:
                if econ_details["itemTargetId"] in self.queued_items:
                    self.queued_items.remove(econ_details["itemTargetId"])
                connection.clean()
            finally:
                if econ_details["itemTargetId"] in self.queued_items:
                    self.queued_items.remove(econ_details["itemTargetId"])
                connection.clean()
            time.sleep(self.buy_debounce)
            

    def watcher(self):
        cookie = self.details_cookie

        while True:
            if len(self.items) > 0:
                try:
                    start = time.time()
                    buyer_threads = []
                    
                    self.session.headers = {
                        "x-csrf-token": cookie["auth"],
                        "cache-control": "no-cache",
                        "pragma": "no-cache"
                    }
                    conn = self.session.post("https://catalog.roblox.com/v1/catalog/items/details", json={ "items": self.items }, verify=False)
                    data = conn.json()
                    self.latency = round(time.time() - start, 2)
                    if conn.status_code == 200:
                        self.checks += 1

                        if("data" in data):
                            for item in data["data"]:
                                if ("unitsAvailableForConsumption" in item and item["unitsAvailableForConsumption"] > 0) and not item["saleLocationType"] == "ExperiencesDevApiOnly" and not item["id"] in self.queued_items and not item["id"] in self.blacklist:
                                    if item["price"] > 0 and self.only_free:
                                        continue
                                    
                                    if(item["price"] <= 0):
                                        threading.Thread(target=self.post_free_item, args=(item["collectibleItemId"],)).start()

                                    try:
                                        d_conn = self.details_connection.get()
                                        d_conn.request(
                                            method="POST",
                                            url="/marketplace-items/v1/items/details",
                                            body='{"itemIds":["%s"]}' % (item["collectibleItemId"]),
                                            headers={"Content-Type": "application/json", "Cookie": ".ROBLOSECURITY=%s" % cookie["cookie"], "x-csrf-token": cookie["auth"]}
                                        )
                                        d_resp = d_conn.getresponse()
                                        d_data = json.loads(d_resp.read())[0]

                
                                        for client_cookie in self.buyer_cookies:
                                            thread = threading.Thread(target=self.buyer, args=(self.buyer_cookies[client_cookie], self.buyer_connections[client_cookie], d_data, "watcher",))
                                            buyer_threads.append(thread)
                                            thread.start()

                                    except Exception as error:
                                        print("Errror while attempting purchase (watcher)", error)
                                    finally:
                                        self.details_connection.clean()
                    elif conn.status_code == 403:
                        self.refresh_tokens()
                except Exception as error:
                        self.errors += 1
                        print("Watcher", error)
                        pass
                time.sleep(self.scan_speed)
            else:
                time.sleep(1)

    def legacy_watcher(self, id):
        cookie = self.details_cookie  

        while True:
            try:
                start = time.time()
                buyer_threads = []

                self.session.headers = {
                    "x-csrf-token": cookie["auth"],
                    "cache-control": "no-cache",
                    "pragma": "no-cache"
                }
                conn = self.session.get(f"https://economy.roblox.com/v2/assets/{id}/details", verify=False)
                data = conn.json()
                self.latency = round(time.time() - start, 2)
                if conn.status_code == 200:
                    self.checks += 1
                    if data["IsForSale"] == True and ("Remaining" in data and data["Remaining"] > 0) and data["SaleLocation"]["SaleLocationType"] == 5 and not data["AssetId"] in self.queued_items and not data["AssetId"] in self.blacklist:
                        if ("PriceInRobux" in data and data["PriceInRobux"] > 0) and self.only_free:
                            continue

                        if("PriceInRobux" in data and data["PriceInRobux"] <= 0):
                            threading.Thread(target=self.post_free_item, args=(data["CollectibleItemId"],)).start()

                        compressed_data = {
                            "collectibleItemId": data["CollectibleItemId"],
                            "collectibleProductId": data["CollectibleProductId"],
                            "creatorId": data["Creator"]["Id"],
                            "name": data["Name"],     
                            "price": data["PriceInRobux"],
                            "itemTargetId": data["AssetId"]                       
                        }

                        for client_cookie in self.buyer_cookies:
                            thread = threading.Thread(target=self.buyer, args=(self.buyer_cookies[client_cookie], self.buyer_connections[client_cookie], compressed_data, "legacy watcher"))
                            buyer_threads.append(thread)
                            thread.start()

                elif conn.status_code == 403:
                    self.refresh_tokens()
            except Exception as error:
                self.errors += 1
                print("Legacy Watcher", error)
                pass
            time.sleep(self.scan_speed)
     


if __name__ == '__main__':
    Client()
