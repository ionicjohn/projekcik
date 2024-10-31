import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';


const PersonList = ({ onEdit }) => {
   const [people, setPeople] = useState([]);
   const [error, setError] = useState(null);


const fetchPeople = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/people/', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if(!response.ok) {
      throw new Error(`HTTP Error! status: ${response.status}`)
    }

    const data = await response.json();
    setPeople(data.data || []);
  } catch (err){
    setError('Failed to fetch people: ' + err.message);
    console.error('Fetch error:', err)
  }
};




}






function App() {
  return (
    <div className="App">

    </div>
  );
}

export default App;
