// ws-test.js
const express = require("express");
const path = require("path");

const app = express();
const PORT = 40001;

const WS_URL = "ws://directable-connie-addedly.ngrok-free.dev/videos/jobs/";

app.use(express.static(path.join(__dirname)));

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
  console.log(`🔌 Default WS URL: ${WS_URL}`);
});
