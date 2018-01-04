#############################################################
#################### START ADDON IMPORTS ####################
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import os
import re
import sys
import urllib
import urllib2
import urlparse
import Main
import json
import base64
import time
from datetime import datetime


import pyxbmct.addonwindow as pyxbmct
from addon.common.addon import Addon

dialog = xbmcgui.Dialog()



#############################################################
#################### SET ADDON ID ###########################
_addon_id_  = 'plugin.video.area51x'
_self_  = xbmcaddon.Addon(id=_addon_id_)
icon  = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_, 'icon.png'))
username = _self_.getSetting('Username')
password = _self_.getSetting('Password')
baseurl = base64.b64decode('aHR0cDovL2lwdHYtYXJlYS01MS50djoyMDk1Lw==')
livecatapi = ('player_api.php?username=%s&password=%s&action=get_live_categories' %(username,password))
livechanapi = ('player_api.php?username=%s&password=%s&action=get_live_streams&category_id=' %(username,password))
vodsapi = ('player_api.php?username=%s&password=%s&action=get_vod_streams' % (username,password))
vodcats = ('player_api.php?username=%s&password=%s&action=get_vod_categories' % (username,password))
vodcatsstream = ('player_api.php?username=%s&password=%s&action=get_vod_streams&category_id=' % (username,password))
epgapi = ('/player_api.php?username=%s&password=%s&action=get_short_epg&stream_id=' %(username,password))
adultpassword = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ , 'adult.txt'))
AddonTitle = '[COLOR green]Area 51 X[/COLOR]'
global username
global password

#############################################################
#################### SET ADDON THEME DIRECTORY ##############
_theme_ = _self_.getSetting('Theme')
_images_    = '/resources/' + _theme_	

#############################################################
#################### SET ADDON THEME IMAGES #################
Background_Image    = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'listbg51.gif'))
Listbg = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'listbg.png'))
Addon_Image = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'icon.png'))
#MainMenu = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'mainmenu.png'))
#MainMenuF = xbmc.translatePath(os.path.join('special://home/addons/' + _addon_id_ + _images_, 'mainmenuF.png'))




########## Function To Call That Starts The Window ##########
def listwindow(ta):
    
    global data
    global List
    
    data = ta
    window = list_window('area51x')
    window.doModal()

    del window

def Get_Data(url):

    req = urllib2.Request(url)
    req.add_header(
        'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
    response = urllib2.urlopen(req, timeout=30)
    data = response.read()
    response.close()

    return data
    
def Time_Clean(text):

    text=str(text)
    d = datetime.strptime(text, "%H:%M")
    converted = d.strftime("%I:%M %p")
    return converted
    
def Adult_Check():
    
    readadult = open(adultpassword).read().replace('\n', '').replace('\r','').replace('\t','')
    if readadult == '':
        dialog.ok(AddonTitle,"[COLOR green]Please Enter A Password To Prevent Unauthorized Access[/COLOR]")
        string =''
        keyboard = xbmc.Keyboard(string, 'Enter The Password You Set')
        keyboard.doModal()
        if keyboard.isConfirmed():
            string = keyboard.getText()
            if len(string)>1:
                term = string
            else: quit()
        with open(adultpassword, "w") as output:
            output.write(term)
            dialog.notification(AddonTitle, '[COLOR yellow]Password Saved, Thank you[/COLOR]', icon, 5000)
            Main.MainWindow
    else:
        string =''
        keyboard = xbmc.Keyboard(string, '[COLOR green]Enter The Password You Set[/COLOR]')
        keyboard.doModal()
        if keyboard.isConfirmed():
            string = keyboard.getText()
            if len(string)>1:
                term = string
            else: quit()
        if term == readadult:
            return
        elif term == 'wipemypass':
            with open(adultpassword, "w") as output:
                wipe = ''
                output.write(wipe)
                dialog.ok(AddonTitle, '[COLOR yellow]Master Pass entered\nPassword has now been wiped clean\nHit back and re enter a new password[/COLOR]')
                quit()
                
        else:
            dialog.notification(AddonTitle, '[COLOR yellow]Wrong Password, I\'m Telling Mum!, Click back to exit[/COLOR]', icon, 5000)
            quit()
    
    
def CLEANUP(text):

    text = str(text)
    text = text.replace('\\r','')
    text = text.replace('\\n','')
    text = text.replace('\\t','')
    text = text.replace('\\','')
    text = text.replace('<br />','\n')
    text = text.replace('<hr />','')
    text = text.replace('&#039;',"'")
    text = text.replace('&#39;',"'")
    text = text.replace('&quot;','"')
    text = text.replace('&rsquo;',"'")
    text = text.replace('&amp;',"&")
    text = text.replace('&#8211;',"&")
    text = text.replace('&#8217;',"'")
    text = text.replace('&#038;',"&")
    text = text.replace('&#8211;',"-")
    text = text.lstrip(' ')
    text = text.lstrip('	')

    return text

def passed(self, title):

    global Item_Title
    global Item_Link
    global Item_Desc
    global Item_Icon

    Item_Title =  []
    Item_Link  =  []
    Item_Desc  =  []
    Item_Icon  =  []
    
    
    
    if 'Live' in title:
        title = title.upper()
        Item_Title.append('[COLOR yellow]' + title + '[/COLOR]')
        Item_Link.append('')
        Item_Desc.append('Area 51 X :: http://area-51-hosting.host/')
        Item_Icon.append(Addon_Image)
        self.List.addItem('[COLOR red]' + title + ' Channel Catergories' + '[/COLOR]')
        self.textbox.setText('Area 51 X :: http://area-51-hosting.host/')
        self.Show_Logo.setImage(Addon_Image)
        url = baseurl + livecatapi
        link = Get_Data(url)
        data = json.loads(link)
        for i in data:
            catname = i['category_name']
            Item_Title.append(catname)
            Item_Desc.append(catname)
            catid = i['category_id']
            catid ='CAT:' + catid
            Item_Link.append(catid)
            self.List.addItem(catname)
            
    elif 'Vod' in title:
        title = title.upper()
        Item_Title.append('[COLOR yellow]' + title + '[/COLOR]')
        Item_Link.append('')
        Item_Desc.append('Area 51 X :: http://area-51-hosting.host/')
        Item_Icon.append(Addon_Image)
        self.List.addItem('[COLOR red]' + 'Videos On Demand Catergories'  + '[/COLOR]')
        self.textbox.setText('Area 51 X :: http://area-51-hosting.host/')
        self.Show_Logo.setImage(Addon_Image)
        url = baseurl + vodcats
        link = Get_Data(url)
        data = json.loads(link)
        for i in data:
            catid = i['category_id']
            catname = i['category_name']
            Item_Title.append(catname)
            Item_Desc.append(catname)
            conurl = 'VODCATS:' + baseurl + vodcatsstream + str(catid)
            Item_Link.append(conurl)
            self.List.addItem(catname)

def List_Selected(self):
    global Media_Link
    
    if 'CAT:' in Media_Link:
        self.List.reset()
        self.List.setVisible(True)
        global Item_Title
        global Item_Link
        global Item_Desc
        global Item_Icon
        
        Item_Title =  []
        Item_Link  =  []
        Item_Desc  =  []
        Item_Icon  =  []
        titles = []
        epgs = []
        streams = []
        icons = []
        combined = []
        
        if 'ADULT' in Media_Title:
            Adult_Check()
        
        newlink = Media_Link.replace('CAT:','')
        title = 'Live Channels'
        Item_Title.append('[COLOR yellow]' + title + '[/COLOR]')
        Item_Link.append('')
        Item_Desc.append('Area 51 X :: http://area-51-hosting.host/')
        Item_Icon.append(Addon_Image)
        self.List.addItem('[COLOR red]' + title  + '[/COLOR]')
        
        url = baseurl + livechanapi + newlink
        link = Get_Data(url)
        data = json.loads(link)
        dialog.notification("[COLOR green]Loading Channels and EPG Data[/COLOR]", '[COLOR red]Please Wait[/COLOR]', Addon_Image, 50000)
        
        for i in data:
            desc = ''
            decode = ''
            channame = i['name']
            titles.append(channame)
            #Item_Title.append(channame)
            streamid = i['stream_id']
            streamid2 = str(streamid)
            streamdes = i ['stream_type']
            epg = baseurl + epgapi + streamid2
            getepg = Get_Data(epg)
            data2 = json.loads(getepg)
            info = data2['epg_listings']
            if len(info) == 0:
                epgguide = 'No EPG Available For This Channel'
                epgs.append(epgguide)
                #Item_Desc.append(epgguide)
            else:
                for info2 in info[:1]:
                    start = info2['start']
                    end = info2 ['end']
                    guidedata = info2['description']
                    title = info2['title']
                    decodetitle = base64.b64decode(title)
                    decodeguide = base64.b64decode(guidedata) + '\n\n'
                    starttime = str(start)[:-3].split(' ')[1]
                    endtime = str(end)[:-3].split(' ')[1]
                    starttime = Time_Clean(starttime)
                    endtime = Time_Clean(endtime)
                    desc = 'Start: ' + starttime + " End: " + endtime + '\n\n' + '[COLOR white]' + decodetitle + '[/COLOR]' + '\n\n' + decodeguide
                    desc1 = str(desc)
                    epgs.append(desc1)
                    #Item_Desc.append(desc)
            channellogo = i ['stream_icon']
            icons.append(channellogo)
            #Item_Icon.append(channellogo)
            playlink = 'PLAY:' + baseurl + streamdes + '/' + username + '/' + password + '/' + streamid2 + '.m3u8'
            streams.append(playlink)
            #Item_Link.append(playlink)
            combined = list(zip(titles,epgs,streams,icons))
        tup = sorted(combined,reverse=False)
        for chantitle,epginfo,playlinks,chanlogos in tup:
            Item_Title.append(chantitle)
            Item_Desc.append(epginfo)
            Item_Link.append(playlinks)
            Item_Icon.append(chanlogos)
            self.List.addItem(chantitle)
        xbmc.executebuiltin("Dialog.Close(dialog)")
        dialog.notification("[COLOR green]All Done[/COLOR]", '[COLOR red]Thank You[/COLOR]', Addon_Image, 2500)
        
    if 'VODCATS:' in Media_Link:
        self.List.reset()
        self.List.setVisible(True)
        global Item_Title
        global Item_Link
        global Item_Desc
        global Item_Icon
        
        Item_Title =  []
        Item_Link  =  []
        Item_Desc  =  []
        Item_Icon  =  []
        title = 'VOD\'s'
        title = title.upper()
        Item_Title.append('[COLOR yellow]' + title + '[/COLOR]')
        Item_Link.append('')
        Item_Desc.append('Area 51 X :: http://area-51-hosting.host/')
        Item_Icon.append(Addon_Image)
        self.List.addItem('[COLOR red]' + 'Videos On Demand'  + '[/COLOR]')
        self.textbox.setText('Area 51 X :: http://area-51-hosting.host/')
        self.Show_Logo.setImage(Addon_Image)
        Media_Link = Media_Link.replace('VODCATS:','')
        link = Get_Data(Media_Link)
        data = json.loads(link)
        for i in data:
            title = i['name']
            Item_Title.append(title)
            Item_Desc.append(title)
            streamid = i['stream_id']
            streamtype = i['container_extension']
            streamdes = i['stream_type']
            playurl = 'PLAY:' + baseurl + streamdes + '/' + username + '/' + password + '/' + str(streamid) + '.' + streamtype
            icon = i ['stream_icon']
            Item_Icon.append(icon)
            Item_Link.append(playurl)
            self.List.addItem(title)
    if 'PLAY' in Media_Link:
        Media_Link = Media_Link.replace('PLAY:','')
        Show_List  =  xbmcgui.ListItem(Media_Title)
        xbmc.Player().play(Media_Link, Show_List, False)
            
            
            


#############################################################
######### Class Containing the GUi Code / Controls ##########
class list_window(pyxbmct.AddonFullWindow):

    xbmc.executebuiltin("Dialog.Close(busydialog)")

    def __init__(self, title='area51x'):
        super(list_window, self).__init__(title)

        self.setGeometry(1280, 720, 100, 50)

        Background  = pyxbmct.Image(Background_Image)

        self.placeControl(Background, -10, -1, 123, 52)

        self.set_info_controls()

        self.set_active_controls()

        self.set_navigation()

        #self.connect(pyxbmct.ACTION_NAV_BACK, lambda:listwindow(data))
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.connect(self.List, lambda:List_Selected(self))
        
        passed(self, data)
        self.setFocus(self.List)


    def set_info_controls(self):
        self.Hello = pyxbmct.Label('', textColor='0xFF00f72c', font='font60', alignment=pyxbmct.ALIGN_CENTER)
        self.placeControl(self.Hello, -4, 1, 1, 50)

        self.textbox = pyxbmct.TextBox(textColor='0xFF00f72c')
        self.placeControl(self.textbox, 74, 27, 22, 19)

        self.Show_Logo = pyxbmct.Image('')
        self.placeControl(self.Show_Logo, 25, 38, 40, 10)


    def set_active_controls(self):
        self.List =	pyxbmct.List(buttonFocusTexture=Listbg,_space=12,_itemTextYOffset=-7,textColor='0xFF00f72c')
        self.placeControl(self.List, 12, 1, 85, 15)
        
        # self.button1 = pyxbmct.Button('',   noFocusTexture=MainMenu, focusTexture=MainMenuF)
        # self.placeControl(self.button1, 65, 26,  9, 8)

        
        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_UP,
             pyxbmct.ACTION_MOUSE_MOVE],
            self.List_update)



    def set_navigation(self):
        pass

    def List_update(self):
        global Media_Title
        global Media_Link
        global Media_Desc
        global Media_Icon

        try:
            if self.getFocus() == self.List:
            
                position = self.List.getSelectedPosition()
                
                Media_Title = Item_Title[position]
                Media_Link  = Item_Link[position]
                Media_Desc = Item_Desc[position]
                
                self.textbox.setText(Media_Desc)
                self.textbox.autoScroll(1000, 1000, 1000)
                
                if Item_Icon[position] is not None:
                    Media_Icon = Item_Icon[position]
                    self.Show_Logo.setImage(Media_Icon)
                else:
                    Media_Icon = 'http://via.placeholder.com/300x220/13b7ff/FFFFFF?text=' + Media_Title
                    self.Show_Logo.setImage(Media_Icon)
                    
        except (RuntimeError, SystemError):
            pass
    
    

