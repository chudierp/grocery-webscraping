from flask import Flask, render_template, request, redirect, url_for 
from pymongo import MongoClient
from bson import ObjectId
import requests
import json
import os

APIKEY='279E16798E440C8B25FBDD277211AFE8A2B2243B2449727999CBB1489836A703'
host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Groceries')
client = MongoClient(host=f'{host}?retryWrites=false')
# db = client.Groceries

db = client.get_default_database()
# groceries = db.groceries
comments = db.comments
groceries_list = db.groceries_list
groceries_list.drop()


# groceries_list.insert_one( { apple_juice })

# groceries_list.insert_one({'title': 'Milk', 'img': '/static/milk.jpg', 'price_walmart': 2.32, 'price_kroger': 1.99, 'price_joe': 2.99, 'lowest_price': 1.99, 'lowest_store': 'Kroger'})
# groceries_list.insert_one({'title': 'Beef', 'img': '/static/beef.jpg'})
# groceries_list.insert_one({'title': 'Bread', 'img': '/static/bread.jpg'})
# groceries_list.insert_one({'title': 'Cake', 'img': '/static/cake.png'})
# groceries_list.insert_one({'title': 'Cheese', 'img': '/static/cheese.jpg'})
# groceries_list.insert_one({'title': 'Chicken', 'img': '/static/chicken.jpg'})
# groceries_list.insert_one({'title': 'Eggs', 'img': '/static/eggs.jpg'})
# groceries_list.insert_one({'title': 'Fish', 'img': '/static/fish.jpeg'})
# groceries_list.insert_one({'title': 'Hotsauce', 'img': '/static/hotsauce.jpeg'})
# groceries_list.insert_one({'title': 'Ketchup', 'img': '/static/Ketchup.jpg'})
# groceries_list.insert_one({'title': 'Macncheese', 'img': '/static/macncheese.jpg'})
# groceries_list.insert_one({'title': 'Ranch', 'img': '/static/Ranch.jpg'})
# groceries_list.insert_one({'title': 'Pasta', 'img': '/static/pasta.jpg'})
# groceries_list.insert_one({'title': 'Rice', 'img': '/static/rice.jpeg'})
# groceries_list.insert_one({'title': 'Tofu', 'img': '/static/tofu.jpg'})

class GroceryItem:

  def __init__(self, title, price_kroger, price_trader_joes, price_walmart, image_link):
    self.title = title
    self.img = image_link

    self.prices = {
      "Kroger": price_kroger,
      "Trader Joes": price_trader_joes,
      "Walmart": price_walmart
    }
  
  def lowest_price(self):

    lowest_price = float("inf")
    store = None

    for k,v in self.prices.items():
      if v < lowest_price:
        lowest_price = v
        store = k

    return (store, lowest_price)
apple_juice = GroceryItem("Apple Juice", 2.32, 3.21, 1.99, '/static/tofu.jpg')
# ornage = GroceryItem("Ornage", 2.32, 3.21, 1.99, '/static/rice.jpeg')
print(apple_juice)

groceries_list.insert_one({'title': apple_juice})
# groceries_list.insert_one({'title': ornage})

app = Flask(__name__)

# @app.route('/')
# def index():
#     """Return homepage."""
#     return render_template('home.html', msg='contractor project')

# groceries = [
#     { 'title': 'Dairy, Cheese, and Eggs', 'description': 'Cats acting weird' },
#     { 'title': '80\'s Music', 'description': 'Don\'t stop believing!' }
# ]

@app.route('/')
def groceries_index():
    """Show all playlists."""
    print(groceries_list)
    return render_template('groceries_index.html', groceries_list = groceries_list.find())

@app.route('/groceries/new')
def groceries_new():
    """Add a new item to groceries list"""
    print(groceries_list.find())
    return render_template('groceries_new.html', groceries_list = groceries_list.find())

@app.route('/groceries', methods=['POST'])
def groceries_submit():
    """Submit a new item to groceries list."""
   
    item = eval(request.form.get('dropdown'))
    print(item)
    groceries_list.insert_one(item)
    
    return redirect(url_for('groceries_index'))

@app.route('/groceries/<grocery_id>')
def groceries_show(grocery_id):
    """Show a single playlist."""
    grocery = groceries_list.find_one({'_id': ObjectId(grocery_id)})
    grocery_comments = comments.find({'grocery_id': ObjectId(grocery_id)})
    item = grocery['title']
    url =  'https://grocerybear.com/getitems'
    headers = {'api-key': APIKEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    print(headers)
    payload = {"city":"SF", "product":item, "num_days": 7}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r)
    return render_template('groceries_show.html', grocery=grocery, comments=grocery_comments)

@app.route('/groceries/<grocery_id>/delete', methods=['POST'])
def groceries_delete(grocery_id):
    """Delete one playlist."""
    groceries_list.delete_one({'_id': ObjectId(grocery_id)})
    return redirect(url_for('groceries_index'))

@app.route('/groceries/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    comment = {
        'content': request.form.get('content'),
        'grocery_id': ObjectId(request.form.get('grocery_id'))
    }
    print(comment)
    comment_id = comments.insert_one(comment).inserted_id
    return redirect(url_for('groceries_show', grocery_id=request.form.get('grocery_id')))                      

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))