// Node server: listens for TCP ventilator data on configured ports,
// forwards raw data to the Python analysis service, and emits results to dashboard clients via Socket.IO
const net = require('net');
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const axios = require('axios');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const HTTP_PORT = process.env.HTTP_PORT || 3000;
const PYTHON_ANALYSIS_URL = process.env.PYTHON_ANALYSIS_URL || 'http://localhost:5000/analyze';
const VENT_PORTS = process.env.VENT_PORTS ? process.env.VENT_PORTS.split(',').map(Number) : [9001,9002];

// Keep latest state per port
const latestByPort = {};

io.on('connection', socket => {
  console.log('Dashboard client connected');
  // send initial state
  socket.emit('initial', latestByPort);
});

async function analyzeAndEmit(port, raw) {
  try {
    const resp = await axios.post(PYTHON_ANALYSIS_URL, { raw, port });
    const result = resp.data;
    latestByPort[port] = { raw, result, ts: Date.now() };
    io.emit('vent-data', { port, raw, result });
  } catch (err) {
    console.error('Error calling analysis service:', err.message || err);
  }
}

function startTcpListener(port) {
  const server = net.createServer((socket) => {
    console.log(`TCP client connected on port ${port}`);
    socket.on('data', (chunk) => {
      const raw = chunk.toString().trim();
      console.log(`Received on port ${port}:`, raw);
      analyzeAndEmit(port, raw);
    });
    socket.on('error', (err) => console.error('Socket error:', err));
    socket.on('close', () => console.log(`TCP client disconnected on port ${port}`));
  });
  server.on('error', (err) => console.error(`Listener error on port ${port}:`, err));
  server.listen(port, () => console.log(`Listening for ventilator data on TCP port ${port}`));
}

for (const p of VENT_PORTS) startTcpListener(p);

server.listen(HTTP_PORT, () => {
  console.log(`HTTP + Socket.IO server running on http://localhost:${HTTP_PORT}`);
  console.log(`Forwarding raw data to Python analysis at ${PYTHON_ANALYSIS_URL}`);
});
