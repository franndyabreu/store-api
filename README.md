# Shopify Challenge Question API

## Usage

All responses will have the form

```json
{
    "data": "Mixed type holding the content of the response",
    "message": "Description of what happened"
}
```


### List all orders

**ROUTE**

`GET /orders`

**Response**

- `200 OK` on success.

```json
{
    "data":[{
        id:
        store_id:
        total_price:
    },
        {line_items: [
            id:
            name:
            unit_price:
           quantity:
        ]
    }
    ]
}

```

### Register a new store

**ROUTE**

`POST /add/store`

**Arguments**

- `"id":int` Unique identifier for this store.
- `"name":string` A name for this store.
- `"address":string` The location of this store.


**Response**

- `201 Created` on success.


## Get a specific store information

**ROUTE**
`GET /store/<id>`

**Arguments**
- `"id:int` Unique identifier for this store.

**Response**

- `404 Not Found` if the store does not exist.
- `200 OK` on success.

```json
{
    "data": [ {"Store Information" }]
}
```

## Lookup orders for a specific store

**ROUTE**

`GET /store/<id>/orders`

**RESPONSE**

-`404 Not found` if the store id does not exist.
-`200 Ok` on success.

## Delete an existing order

**ROUTE**

`DELETE /store/<id>/delete/order/<order_id>`

**Arguments**
- `"id:int` Unique identifier for this store.
- `"order_id:int` Unique identifier of an existing order.

**RESPONSE**

-`404 Not found` If the store or order id does not exist.
-`204 No content` on success.


## Delete a store

**ROUTE**

`DELETE /delete/store/<id>`

**Arguments**

- `"id":int` Unique identifier for this store.

**Response**

- `404 Not Found` if the store id does not exist.
- `204 No Content` on success.

## Add a product to a store.

**ROUTE**

`POST /store/<id>/add/product`

**Arguments**

- `"id":int` Unique identifier for this store.
- `"product_id":int` Unique identifier for the product.
- `"product_name":string` Name of the product.
- `"product_price":float` Price of the product.
- `"quantity":int` Amount.

**Response**
- `201 Content Created` if the product exists, the quantity will be updated. 
-`404 Not found` If the store id does not exist.


## Buy a product from store

**ROUTE**

`POST /store/<id>/buy/product`

**Arguments**
- `"id":int` Unique identifier for this store.
- `"product_id":int` Unique identifier for this product.
- `"quantity":int` Amount.
-`"order_id":int` Unique identifier for the generated order.

**Response**

-`204 No content` If the quantity of the product is 0 or less than the quantity ordered by the user.
-`404 Not found` If the product or the order id does not exist.
-`200 Ok` On sucess. An order will be generated > `/store/<id>/orders`.

## Delete an existing product

**ROUTE**
`DELETE /store/<id>/delete/product/<product_id>`

**Arguments**
- `"id":int` Unique identifier for this store.
- `"product_id":int` Unique identifier for the product.

**Response**
- `204 No content` on sucess.
-`404 Not found` If the store id or the product id does not exist.