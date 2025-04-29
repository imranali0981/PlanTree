import express from "express";
import SensorData from "../models/SensorData.js";

const router = express.Router();

router.post("/", async (req, res) => {
  const { location, temperature, humidity, mq135 } = req.body;

  try {
    const newData = new SensorData({
      location,
      temperature,
      humidity,
      mq135,
    });

    newData
      .save()
      .then((data) => console.log("Data submit succesfully", data))
      .catch((err) => res.status(500).json(err));
  } catch (e) {
    console.log("Error occured while trying to send the data", e);
  }
});

router.get("/", async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 100;
    const skip = (page - 1) * limit;

    const Datasensor = await SensorData.find().skip(skip).limit(limit);
    const total = await SensorData.countDocuments();
console.log("Total documents:", total);
    console.log("Current page:", page);

    res.status(200).json({
      total,
      page,
      limit,
      data: Datasensor,
    });
  } catch (e) {
    console.log("Error occurred", e);
    res.status(500).json({ message: "Unable to fetch data from database", e });
  }
});

export default router;
