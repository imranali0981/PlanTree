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

// get latest data by location
router.get("/latest/:location", async (req, res) => {
  const { location } = req.params;
  try {
    const latest = await SensorData.findOne({ location }).sort({
      timestamp: -1,
    });

    if (!latest) {
      return res.status(404).send({ error: "No data found" });
    }

    console.log("Latest data for location:", location);
    console.log("Latest data:", latest);
    res.send({
      temperature: latest.temperature,
      humidity: latest.humidity,
      mq135: latest.mq135,
    });
  } catch (error) {
    console.error("Error fetching latest data:", error);
    res.status(500).send({ error: "Internal server error" });
  }
});

export default router;
