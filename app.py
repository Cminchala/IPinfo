from flask import Flask, render_template, url_for, request, redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from requests import get
import json
import requests
from whoisapi import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ipdata.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)



class IPS(db.Model): ## Create Database
    id = db.Column(db.Integer, primary_key = True)  #ID
    ip = db.Column(db.String(200), nullable = False) #IP
    date_create = db.Column(db.DateTime, default=datetime.utcnow)#DateTime

    def __repr__(self):
        return '<IP %r>' % self.ip
  
  



@app.route("/<ip_address>", methods = ["GET","POST"])
def curl(ip_address): ## Return ip data from 
   
    if request.method == 'GET':
        urls = "http://ip-api.com/json/"
       
        urls += ip_address
        resp = requests.get(urls) 
      
        ipdata = json.loads(resp.text)
        ips = ipdata
        if ipdata['status'] == "success":
             ipdatas = IPS(ip=ip_address)
             db.session.add(ipdatas)
             db.session.commit()

        return ipdata
    else:
       return redirect('/ipinfo')


   


@app.errorhandler(404) ##
def page_not_found(e):
    return redirect("/ipinfo")


@app.route('/ipinfo', methods=["GET", "POST"])
def ipInfo():
    urls = "http://ip-api.com/json/"
    iper = {}
    ipd = ""
    if request.method == "POST":
        ipe = request.form.get("ip") ## get URL form into HTML 
        if ipe == '':
            return "No IP Go Back and Enter a IP"
        ipd = ipe
        
        
        urls += ipd ##adds the url and ip together
        resp = requests.get(urls)
        ipdata = json.loads(resp.text)
       
        iper = ipdata
        if iper['status'] == "success":
             ipdatas = IPS(ip=ipd)
             db.session.add(ipdatas)
             db.session.commit()
      
       
        return render_template("ipInfo.html", show_ip=iper)
    return render_template('ipInfo.html',show_ip = iper)
    


@app.route('/map/',methods = ['GET','POST'])  #done
def mapInfo():
       try:   
        lat = 0.0
        long = 0.0
        country = ''
        urls = "http://ip-api.com/json/"
        if request.method == "POST":
          iptomap = request.form.get("mapIP")
          ip = iptomap
          if ip == '':
              return "No IP Go Back and Enter a IP"
          
          urls += ip
          resp = requests.get(urls)
          data = json.loads(resp.text) ###### #####
        
          lat = data['lat']
          long = data['lon']
          country = data['country']
       except KeyError:
              return "No Location Found "
          
       return render_template("map.html",newlat= lat,newlong = long,region = country)
       return render_template("map.html",newlat= lat,newlong = long,region = country)

@app.route('/whois/', methods=['GET', 'POST']) #DONE
def whoIs():
    
    final = {}
    if request.method == "POST":
        ipe = request.form.get("whoisip")
        
        client = Client(api_key='at_T9t1Z67gZSNYozqSy88VT0XuSaU6p')
        client.parameters.output_format = 'json'
        
        final = json.loads(client.raw_data(ipe))

        return render_template("whois.html",show_whois = final)
    return render_template("whois.html",show_whois = final)


@app.route("/log/")
def logs():
    ipdata = IPS.query.order_by(IPS.date_create.desc()).all()
    return render_template("logs.html",ipdata = ipdata)


if __name__ == "__main__":
    # db.create_all
    app.run(debug =True)

