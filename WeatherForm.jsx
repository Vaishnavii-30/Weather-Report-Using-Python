// simplified
import { useState } from "react";

export default function WeatherForm({ onResult }) {
  const [city, setCity] = useState("");

  function validCity(name){
    return name && name.trim().length >= 2;
  }

  async function handleSubmit(e){
    e.preventDefault();
    if(!validCity(city)) return alert("Enter a valid city name (min 2 chars).");
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    if(!res.ok) return alert("Error fetching weather");
    const data = await res.json();
    onResult(data);
  }

  async function useGeolocation(){
    if(!navigator.geolocation) return alert("Geolocation not supported");
    navigator.geolocation.getCurrentPosition(async pos => {
      const { latitude, longitude } = pos.coords;
      const res = await fetch(`/api/forecast?lat=${latitude}&lon=${longitude}`);
      const data = await res.json();
      onResult({geo:true, ...data});
    }, err => alert("Location denied or unavailable"));
  }
fetch('/api/weather?city=…')
  return (
    <form onSubmit={handleSubmit}>
      <input value={city} onChange={e=>setCity(e.target.value)} placeholder="City name"/>
      <button type="submit">Get Weather</button>
      <button type="button" onClick={useGeolocation}>Use my location</button>
    </form>
  );
}
