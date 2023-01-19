# cs50x-finalproject

# DFTrack
#### Video Demo:  https://www.youtube.com/watch?v=7Lu2r-NeFHo
# Description

Hello World!

I present to everyone DFTrack, a web application built in Flask that tracks prices from the Dafiti website.

*[Dafiti](https://www.cbinsights.com/company/dafiti) is a multi-label fashion e-commerce retailer that specializes in apparel, shoes, accessories, beauty and home decor. Started in Brazil, it operates in five countries across Latin America: Brazil, Argentina, Chile, Colombia, and Mexico.*

By logging into DFTrack, it is possible to create a WishList, with products from the Dafiti website, which can be added by pasting the product link. From there, the user will be able to follow the price of the desired products and will be able to be notified by email as soon as the product is costing a value less than or equal to a value specified by them. Users will thus be able to take advantage of the opportunity to buy what they want at a more affordable price.

*The web app uses some functions provided by the CS50 team in Problem Set 9 (Finance).*


# Python files

In app.py are the routes of the web application. We first Configure application, Ensure templates are auto-reloaded, Configure session to use filesystem (instead of signed cookies), and open a database site.db.

An asynchronous function, BackgroundScheduler, is used to check prices every 24 hours. In the asynchronous route, automatic emails are sent if the price is equal to or below the desired price.

In forms.py a new class is created, RegisterForm. Functions from the flask_wtf library are used. User validation form.

# SQLite

from the site.db database 6 tables are used:
- users, table that stores usernames, users id and password hash
- emails_cadastrados, table that stores the emails address
- lista, table that stores product title, info and product id
- lista_de_links, table that stores the products link
- historico_de_precos, table that stores price history
- precos_desejados, table that stores the expected prices


# HTML files

In the templates folder are the html files used, stylized with Bootstrap:
- 'include' folder contains a modal, stylized with Bootstrap. This responsive poup is used to display extra content, like the title of the product and the date of when the user added the product to the wishlist.
- apology.html was provided by the CS50 team in Problem Set 9 (Finance). It is a template for an apology. apology in helpers.py took two arguments: message, and, optionally, code, which was passed to render_template as the value of top.
- att.py is a form to update the product title description
- email_body is the automatic email template
- email.hmtl
- inicial.html
- layout.html
- login.html
- price-information.html
- prices.html
- register.html
- userreepetido.html
- wishlist.html

In the static folder we find the CSS file, javascript file and images used in the app.


# JavaScript file

Puppeteer communicates with the browser using DevTools Protocol.


