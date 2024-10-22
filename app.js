import express from "express";
import mongoose from "mongoose";
import bodyParser from "body-parser";
import cors from "cors";
import dotenv from "dotenv"; // <-- Updated import for dotenv
import sensorDataRoute from "./routes/sensorDataRoute.js";

dotenv.config();

const app = express();

// const mongoURI =
//   "mongodb+srv://imranali529081:imrankhan@cluster0.kbv5i.mongodb.net/plantree?retryWrites=true&w=majority&appName=Cluster0";

app.use(bodyParser.json());
app.use(cors());
app.use(express.json());

// database connection
mongoose
  .connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("MongoDB connected successfully"))
  .catch((err) => console.log(err));

app.use("/sensor-data", sensorDataRoute);

// 172.16.71.134

// ("mongodb+srv://imranali529081:<db_password>@cluster0.kbv5i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0");

export default app;
