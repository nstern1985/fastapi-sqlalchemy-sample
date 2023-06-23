title multi channel cart

customer->react-app: the customer uses the app to add/remove items from his cart (online store) with shipping details
customer -> store:the customer goes into the store and pickup / remove items from his cart with shipping details
store->serverAPI: update cart metadata
react-app ->serverAPI: update cart metadata
serverAPI -> DB: create/updates the customer's cart
customer ->react-app: closes the deal
customer ->store: closes the deal
store->serverAPI: change order status to approved
react-app ->serverAPI: change order status to approved
serverAPI-> DB:update order status
serverAPI-> deliver-orchastature: order data
deliver-orchastature->queue: items with the same shipping date
queue->deliver-worker:takes an entry from the queue ack when he finished