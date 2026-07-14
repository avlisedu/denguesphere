import { BrowserRouter, Route, Routes } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import Coordenadas from "./pages/Coordenadas";
import Clusterizador from "./pages/Clusterizador";
import Sobre from "./pages/Sobre";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="shell">
        <Sidebar />
        <main className="app-container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/coordenadas" element={<Coordenadas />} />
            <Route path="/clusterizador" element={<Clusterizador />} />
            <Route path="/sobre" element={<Sobre />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
