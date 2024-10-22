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

export default router;
