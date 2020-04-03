// PRZ comment

const express = require('express')
const app = express()
const port = 3000

app.use(express.json())

const DB = []
let nextID = 1

function getItemByID(id) {
    return DB.filter(x => x.id === id)
}

function addItem(item) {
    item.id = nextID
    nextID++
    DB.push(item)
    return item.id
}

app.get('/', (req, res) => {
    console.log("get / called")
    res.json(DB)
})

app.post('/', (req, res) => {
    console.log("post / called", req.body)
    const id = addItem(req.body)

    res.json({
        id
    })
})

app.get('/:id', (req, res) => {
    console.log("get:/id called", req.params.id)
    res.json(getItemByID(parseInt(req.params.id)))
})

app.put('/:id', (req, res) => {
    const id = parseInt(req.params.id)
    const newItem = req.body
    console.log("put:/id called", id)
    
    let items = getItemByID(id)
    if (items.length) {
        let item = items[0]
        Object.keys(newItem).forEach(k => {
            item[k] = newItem[k]
        })
        res.json(item)
    } else {
        res.json([])
    }
})

app.delete('/:id', (req, res) => {
    const id = parseInt(req.params.id)
    const newItem = req.body
    console.log("Delete:/id called", id)
    DB.splice(id,1)
    res.json([])
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
// app.listen(port, '0.0.0.0')
