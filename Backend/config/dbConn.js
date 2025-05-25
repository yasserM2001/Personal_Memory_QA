// the code is used to connect to the database
const mongoose = require("mongoose");

const connectDB = async()=>{
    try{
        await mongoose.connect(process.env.DATABASE_URI);

    }catch(err){
        console.log(err)

    }

};

module.exports= connectDB;