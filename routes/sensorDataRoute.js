import express from "express";
import SensorData from "../models/SensorData.js";
import axios from "axios";

const router = express.Router();

router.post("/", async (req, res) => {
  const { location, temperature, humidity, mq135 } = req.body;
  console.log("Yahan tk to arha hai sahi se");

  try {
    const pythonResponse = await axios.post(
      "http://192.168.100.94:5000/predict",
      { temperature, humidity, mq135 },
      { timeout: 10000 }
    );

    console.log("Python Response:", pythonResponse.data);
    if (!pythonResponse.data || pythonResponse.data.cluster === undefined) {
      return res
        .status(500)
        .json({ message: "Error: No cluster data received" });
    }

    const newData = new SensorData({
      location,
      temperature,
      humidity,
      mq135,
      label: pythonResponse.data.cluster,
    });

    console.log("Saving to DB:", newData);

    await newData
      .save()
      .then((savedData) => {
        console.log("✅ Data saved successfully:", savedData);
        console.log("Sending response to client...");
        res
          .status(201)
          .json({ message: "Data stored successfully", data: savedData });
      })
      .catch((dbError) => {
        console.error("❌ Error while saving to DB:", dbError);
        res
          .status(500)
          .json({ message: "Database error", error: dbError.toString() });
      });
  } catch (e) {
    console.error("❌ Error in API:", e);
    res.status(500).json({ message: "Server error", error: e.toString() });
  }
});

router.get("/", async (req, res) => {
  try {
    const Datasensor = await SensorData.find();
    res.status(200).json(Datasensor);
  } catch (e) {
    console.log("Error occurred", e);
    res.status(500).json({ message: "Unable to fetch data from database", e });
  }
});

export default router;
