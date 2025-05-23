import mongoose from "mongoose";

const SensorDataSchema = new mongoose.Schema({
  temperature: Number,
  humidity: Number,
  mq135: Number,
  location: String,
  cluster: Number,
  timestamp: {
    type: Date,
    default: Date.now,
  },
});

export default mongoose.model("SensorData", SensorDataSchema);
