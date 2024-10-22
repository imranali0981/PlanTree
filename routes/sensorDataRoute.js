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
    const Datasensor = await SensorData.find();
    res.status(200).json(Datasensor);
  } catch (e) {
    console.log("Error occured", e);
    res.status(500).json({ message: "Unable to fetch data from database", e });
  }
});

export default router;
