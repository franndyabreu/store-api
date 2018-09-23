from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_heroku import Heroku

# Flask_App & SQLAlchemy for flask configuration.
app = Flask(__name__)
#Database Configuration              
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/shopifyapi'
heroku = Heroku(app) 
db = SQLAlchemy(app)


''' -Database models.
    -Each class represents a table in SQLAlchemy.
    -Each class member represents a column. '''

#------ DOMAIN CLASSES ------#
class Shop(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(70))                    #When a shop is delete, the child is deleted.
    products = db.relationship('Product', backref="prod", cascade="delete, delete-orphan") 
    orders = db.relationship('Order', backref="ord", cascade="delete, delete-orphan")

class Product(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    # - Represent the relationship between Product table and the Shop table.
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    # - Represent the relationship between Product table and the LineItem table.
    line_item = db.relationship('LineItem', backref="items", cascade="all, delete-orphan")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    # - Represent the relationship between Order table and the Shop table.
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    # - Represent the relationship between Order table and the Shop table.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    # - Represent the relationship between Order table and the LineItem table.
    line_item = db.relationship('LineItem', backref="itemss", cascade="delete, delete-orphan")

class LineItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    # - Connects the Product table with the LineItem table.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


# --- METHODS to RETRIEVE and SAVE DATA. --- #
def look_up_store(id):
    ''' Check if an store exists, if it exists the function will return it.
     If it does not, it will raise an Exception.'''
    store = Shop.query.filter_by(id=id).first()
    if store:
        return store
    else:
        raise Exception()

def look_up_order(id):
    ''' Check if an order exists, if it exists the function will return it.
     If it does not, it will raise an Exception.'''
    order = Order.query.filter_by(id=id).first()
    if order:
        return order
    else:
        raise Exception()

def save(object):
    db.session.add(object)
    db.session.commit()

    
# --- ROUTING ---- #


#Create
@app.route('/add/store', methods=['POST'])
def add_store():
    #Represent the data of the store to be added.
    data = request.get_json()
    ''' It will try to create the store with the id passed in
        if the id already exists it will return a bad request status code.'''
    try:
        new_store = Shop(id=data['id'], name=data['name'], address=data['address'])
        save(new_store)
               
    
    except:
        return jsonify('Store already exist'), 400 #HTTP STATUS CODE 400: BAD REQUEST

    return jsonify({'message ': 'New store added'}), 201 #HTTP STATUS CODE 201: CREATED




@app.route('/store/<id>/add/product', methods=['POST', 'GET'])
def add_product(id):
    try:
        #Represent the data of the product to be added.
        data = request.get_json()
        #Check if the product exists before adding it. 
        product = Product.query.filter_by(id=data['product_id']).first()

        #Check if the store exist. 
        store = look_up_store(id)

        if not product and store:
            new_product = Product(id=data['product_id'], name=data['product_name'],
            price=data['product_price'], 
            quantity=data['quantity'], shop_id=id)
            save(new_product)
            # db.session.add(new_product)
            # db.session.commit()
            return jsonify({'message': 'New product added'}), 201 #HTTP STATUS CODE 201: CREATED
    

        elif (product and store) and (int(id) != product.shop_id):
            ''' If the product does not exists in the store, 
            this new product will be added to this store.'''
            new_product = product
            new_product.shop_id = id
            new_product.quantity = data['quantity']
            save(new_product) 
            # db.session.add(new_product)
            # db.session.commit()
            return jsonify({'message': 'New product added'}), 201 #HTTP STATUS CODE 201: CREATED
        
    
        else:
            product.quantity += data['quantity']
            db.session.commit()
            return jsonify({'message': 'Product already exist in this store. The quantities updated!'}), 400 #HTTP STATUS CODE 201: CREATED
    
    except:
        return jsonify({'message' : 'Could not find store id!'}), 404 #HTTP STATUS CODE 404: RESOURCE NOT FOUND

   #If there is no product, but there is store, the product 
   # will be associated with the store found.

@app.route('/store/<id>/buy/product', methods=['POST'])
def buy_product(id):
    try:
        #Represent the data of the product to be bought.
        data = request.get_json()
        #Check if the product exists. If it does not, it will return a 404 status code.
        product = Product.query.filter_by(id=data['product_id']).first()

        '''Check if the order exists. If it does, it will update the order,
        otherwise, it will create a new one. '''
        order = Order.query.filter_by(id=data['order_id']).first()

        #Check if the store exists
        look_up_store(id)

        if not product:
            return jsonify({'message': 'No product!'}), 404

        #IF THE ORDER EXIST BUT THE PRODUCT.SHOP_ID IS DIFFERENT THAN THAT ORDER.SHOP_ID
        elif (order and product): #and (product.id = order.product_id):

            if product.quantity < data['quantity'] or product.quantity == 0:
                return jsonify({'message': 'Ops! We ran out of supplies.'}), 204
            for item in order.line_item:
                if product.id == item.product_id: #If the product exists in an order, then it will be updated.
                    order.price += product.price
                    order.total_price += product.price * data['quantity']
                    order.product_id = product.id
                    item.quantity += data['quantity']
                    product.quantity -= data['quantity']
                    db.session.commit()
                    return jsonify({'message': 'order updated!'}), 200

            else: #If there is a product and an order but the product is not in the order:
                new_line_item = LineItem(name=product.name, price=product.price, 
                quantity=data['quantity'], product_id=product.id, order_id=data['order_id'])
                product.quantity -= data['quantity']
                order.product_id = product.id #The value of the product_id will be the last item added to the order.
                order.total_price += product.price * data['quantity']
                save(new_line_item)
            

            return jsonify({'message': 'Order updated!'}), 200

        else: # If the product exist but there is no order.
            
            if product.quantity < data['quantity'] or product.quantity == 0:
                return jsonify({'message': 'Ops! We ran out of supplies.'}), 204
                
            new_line_item = LineItem(name=product.name, price=product.price, 
            quantity=data['quantity'], product_id=product.id, order_id=data['order_id'])
            new_order = Order(id=data['order_id'], price=product.price,
                            total_price=product.price * data['quantity'],
                            product_id=product.id, shop_id=product.shop_id, 
                            line_item=[new_line_item])

            product.quantity -= data['quantity']
            db.session.add_all([new_order, new_line_item])
            db.session.commit()
        
            return jsonify({'message':'order placed!'}), 200
    except:
        return jsonify({'message': 'could not find store id!'}), 404
    

#READ/REPORT/UPDATE

@app.route('/', methods=['GET'])
def index():
    return render_template('READMe.html')


@app.route('/orders', methods=['GET'])
def all_orders():
    ''' This function will return all the orders generated in each store'''
    orders = Order.query.all()
    output = []
    for order in orders:
        order_details = {'order_id': order.id, 'store_id': order.shop_id,
         'total_price': order.total_price}
        for item in order.line_item:
            item_details = {'id': item.id, 'name': item.name, 
            'unit_price': item.price, 'quantity': item.quantity}
            #Append values to the same key.
            order_details.setdefault('line_item', []).append(item_details)
        output.append(order_details)
    return jsonify({'data': output})

@app.route('/store/<id>/orders', methods=['GET']) 
def store_orders(id):
    #It will try to get the store by the id entered in the URL, if it does not find the store, 
    # it will raise an attribute error with the message : {'Could not find store id'-}
    try:
        store = look_up_store(id)
        orders = Order.query.filter_by(shop_id=store.id).all()
        output = [] #Represent the result to be returned
        for order in orders: #Iterate through each order
            orders = [{'store_id': order.shop_id, 'order_id': order.id,
            'total_price': order.total_price}] #Represent the order header details.
            for item in order.line_item: #Iterate through every item in an order.
            #Represent the items inside the order header details
                orders+= [{'item_name': item.name, 'quantity': item.quantity, 'unit_price': item.price}]
            print(orders)
            output.append(orders) #Append the object orders to the output list.
    except:
        #Serialize the object[output] to JSON.
        return jsonify({'message': 'could not find store id!'}), 404
    
    return jsonify({'data': output}), 200 #HTTP STATUS CODE 200: OK


@app.route('/store/<id>', methods=['GET']) 
def store(id):
    ''' DISPLAY A DESCRPTION OF THE STORE, INCLUDING THE PRODUCTS. '''
    try:
        data = look_up_store(id)
        output = []
        store_info = []
        products = [] # Represent the information of the products associated with the store id
        for product in data.products:
            products.append({'id': product.id, 'name' : product.name, 'Price': product.price, 
            'Quantity': product.quantity})
        store_info.append([{'store_id': data.id, 'store_name': data.name,
         'store_address': data.address, 'store_products': products}])
        output.append(store_info)
        return jsonify({'data': output}), 200 #HTTP STATUS CODE 200: OK
    except:
        return jsonify('Could not find store id'), 404 #HTTP STATUS CODE 404: RESOURCE NOT FOUND
 

#DELETE
@app.route('/delete/store/<id>', methods=['GET','DELETE'])
def delete_store(id):
    ''' This function delete the store and all the child tables (Products, Orders and Line_item)'''
    try:
        store = look_up_store(id)
        db.session.delete(store) 
        db.session.commit()
        return jsonify({'message': 'store deleted!'}), 204
    except:
        return jsonify({'message': 'could not find store id.'}), 404


@app.route('/store/<id>/delete/order/<order_id>',methods=['DELETE'])
def delete_order(id, order_id):
    ''' If the store or the order cannot be found, an exeption will be raised '''
    try:
        store = look_up_store(id)
        order = look_up_order(order_id)
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'order deleted!'}), 204
    except:
        return jsonify({'message': 'Could not find order id!'}), 404


@app.route('/store/<id>/delete/product/<product_id>', methods=['DELETE'])
def delete_product(id, product_id):
    try:
        store = look_up_store(id)
        product = Product.query.filter_by(id=product_id).first()
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'product deleted!'}), 204
    except:
        return jsonify({'message': 'could not find either product or store id!'})
    
#If the user try to access to an unexisting route, ReadMe.html will be returned.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("READMe.html")

if __name__ == '__main__':
    app.run(debug=True)
    
    