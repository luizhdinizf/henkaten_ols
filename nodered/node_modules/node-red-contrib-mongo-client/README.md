# node-red-contrib-mongo-client
MongoDB client for Node-RED


## Usage
> Please refer to the [mongoDB node driver 'Collection' documentation](http://mongodb.github.io/node-mongodb-native/3.0/api/Collection.html) to read about each operation.


```js
// input
{
    // Any INPUT will be passed to OUTPUT
    payload,
    foo,
    ...
    // If require MongoDb's functions
    require:['ObjectId','MongoError']
    // callback function
    function(_msg, next){
        // _msg: OUTPUT object
        // next: the MongoClient node
    }
}


// OUTPUT object
{
    // Any 'require' functions from INPUT can be accessed by: `db.ObjectId(...)`
    db,
    // If the 'collectionName' is provided:
    collection

    // From INPUT
    payload,
    foo,
    ...
}

```

### function node
```js
msg.collection
    .countDocuments()
    .then( r => node.send({ payload:r }) )

const ObjectId = msg.ObjectId
msg.db.collection('collectionName')
    .find({
        _id: ObjectId('5d2d8fba4e15c14483a71500')
    })
    .toArray()
    .then( r => node.send({ payload:r }) )

```