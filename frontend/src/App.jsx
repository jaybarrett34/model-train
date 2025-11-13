import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ProjectList from './pages/ProjectList';
import XMLEditor from './pages/XMLEditor';
import DataGenerator from './pages/DataGenerator';
import DatasetManager from './pages/DatasetManager';
import TrainingDashboard from './pages/TrainingDashboard';
import ModelExporter from './pages/ModelExporter';
import SizeAnalyzer from './pages/SizeAnalyzer';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ProjectList />} />
          <Route path="/xml-editor" element={<XMLEditor />} />
          <Route path="/generator" element={<DataGenerator />} />
          <Route path="/datasets" element={<DatasetManager />} />
          <Route path="/size-analyzer" element={<SizeAnalyzer />} />
          <Route path="/training" element={<TrainingDashboard />} />
          <Route path="/export" element={<ModelExporter />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
