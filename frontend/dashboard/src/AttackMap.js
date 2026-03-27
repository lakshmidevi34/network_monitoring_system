import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

function AttackMap({ attackers }) {

return (

<MapContainer
center={[20,0]}
zoom={2}
style={{height:"300px",width:"100%"}}
>

<TileLayer
url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
/>

{attackers.map((a,i)=>{

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

</MapContainer>

);

}

export default AttackMap;