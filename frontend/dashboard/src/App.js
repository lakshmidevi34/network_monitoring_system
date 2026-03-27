import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import Chatbot from "./Chatbot";

import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip
} from "recharts";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7"];

function App() {

  const [data, setData] = useState(null);
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {

    const fetchStats = async () => {

      const res = await axios.get("http://localhost:5000/stats");

      setData(res.data);

      setTimeline(prev => [
        ...prev.slice(-20),
        {
          time: new Date().toLocaleTimeString(),
          pps: res.data.packets_per_second
        }
      ]);
    };

    fetchStats();

    const interval = setInterval(fetchStats, 2000);

    return () => clearInterval(interval);

  }, []);

  if (!data) return <h2>Loading Dashboard...</h2>;

  const protocolData = [
    { name: "TCP", value: data.tcp },
    { name: "UDP", value: data.udp },
    { name: "ICMP", value: data.icmp },
    { name: "ARP", value: data.arp },
    { name: "DNS", value: data.dns }
  ];

  return (

    <div className="dashboard">

      <h1>Network Security Operations Center</h1>

      {/* TOP METRICS */}

      <div className="grid">

        <div className="card">
          <h3>Total Packets</h3>
          <div className="metric">{data.total_packets}</div>
        </div>

        <div className="card">
          <h3>Packets / Second</h3>
          <div className="metric">{data.packets_per_second}</div>
        </div>

        <div className="card">
          <h3>Active Alerts</h3>
          <div className="metric">{data.alerts.length}</div>
        </div>

      </div>

      <br />

      <div className="grid">

        {/* LEFT PANEL */}

        <div className="card">

          <h2>Top Source IPs</h2>

          <ul>
            {Object.entries(data.top_ips).map(([ip, count]) => (
              <li key={ip}>{ip} → {count} packets</li>
            ))}
          </ul>

          <h2>Top Destination Ports</h2>

          <ul>
            {Object.entries(data.top_ports).map(([port, count]) => (
              <li key={port}>Port {port} → {count}</li>
            ))}
          </ul>

          <h2>Active Network Devices</h2>

          <ul>
            {Object.entries(data.top_ips).map(([ip]) => (
              <li key={ip}>{ip}</li>
            ))}
          </ul>

        </div>

        {/* CENTER CHARTS */}

        <div>

          <div className="card">

            <h2>Protocol Distribution</h2>

            <div style={{display:"flex",alignItems:"center"}}>

              <PieChart width={250} height={250}>

                <Pie
                  data={protocolData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                >

                  {protocolData.map((entry,index)=>(
                    <Cell key={index} fill={COLORS[index]} />
                  ))}

                </Pie>

                <Tooltip/>

              </PieChart>

              {/* PROTOCOL LABELS */}

              <div style={{marginLeft:"20px"}}>

                {protocolData.map((p,index)=>(

                  <p key={index}>

                    <span style={{
                      display:"inline-block",
                      width:"12px",
                      height:"12px",
                      background:COLORS[index],
                      marginRight:"8px"
                    }}></span>

                    {p.name} : <b>{p.value}</b>

                  </p>

                ))}

              </div>

            </div>

          </div>

          <div className="card">

            <h2>Traffic Timeline</h2>

            <LineChart width={500} height={250} data={timeline}>

              <XAxis dataKey="time" />

              <YAxis />

              <Tooltip />

              <Line type="monotone" dataKey="pps" stroke="#38bdf8" />

            </LineChart>

          </div>
          {/* <h1>ChatBot</h1>
          <Chatbot/> */}

        </div>

        {/* RIGHT PANEL */}

        <div className="card">

          <h2>Security Alerts</h2>

          {data.alerts.length === 0 ? (
            <p>No threats detected</p>
          ) : (
            <ul>

              {data.alerts.map((alert,index)=>{

                let color="green";

                if(alert.severity==="HIGH") color="red";
                if(alert.severity==="MEDIUM") color="orange";

                return(

                  <li key={index} style={{color:color}}>

                    {alert.severity} — {alert.message}

                  </li>

                );

              })}

            </ul>
          )}

          <h2>Detected Attackers</h2>

          {data.attackers.length===0 ? (

            <p>No attackers detected</p>

          )
          :(

            <ul>

              {data.attackers.map((a,index)=>(

                <li key={index} style={{color:"orange"}}>

                  ⚠ {a.ip} — {a.city}, {a.country} ({a.org})

                </li>

              ))}

            </ul>

          )
          }

          {/* <h3>Attacker Map</h3>

          <MapContainer
            center={[20,0]}
            zoom={2}
            style={{height:"300px",width:"100%"}}
          >

            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {data.attackers.map((a,i)=>{

              if(!a.loc) return null;

              const coords=a.loc.split(",");

              return(

                <Marker key={i} position={[coords[0],coords[1]]}>

                  <Popup>

                    <b>{a.ip}</b><br/>

                    {a.city}, {a.country}<br/>

                    {a.org}

                  </Popup>

                </Marker>

              );

            })}

          </MapContainer> */}

        </div>

      </div>

    </div>

  );

}

export default App;