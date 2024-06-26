import React from 'react';
import DataDisplay from './components/DataDisplay';
import GraphDisplay from './components/GraphDisplay';
/*import GraphDisplay from './components/GraphDisplay';*/

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to Sensor Data Dashboard</h1>
        <DataDisplay />
        <GraphDisplay />
      </header>
    </div>
  );
}

export default App;
