import { useState, useEffect } from 'react';
import { Play, StopCircle, GraduationCap, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { trainingApi, huggingfaceApi } from '../services/api';
import useStore from '../store/useStore';

const TrainingDashboard = () => {
  const { currentProject, trainingStatus, setTrainingStatus, datasets } = useStore();
  const [config, setConfig] = useState({
    datasetId: '',
    baseModel: 'meta-llama/Llama-2-7b-hf',
    outputName: 'my-finetuned-model',
    epochs: 3,
    batchSize: 4,
    learningRate: 2e-4,
    loraR: 8,
    loraAlpha: 32,
    loraDropout: 0.1,
    targetModules: ['q_proj', 'v_proj'],
    gradientAccumulation: 4,
    warmupSteps: 100,
    maxSeqLength: 2048,
  });
  const [jobId, setJobId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [modelSearch, setModelSearch] = useState('');
  const [modelResults, setModelResults] = useState([]);

  useEffect(() => {
    let interval;
    if (trainingStatus.isTraining && jobId) {
      interval = setInterval(checkTrainingStatus, 3000);
    }
    return () => clearInterval(interval);
  }, [trainingStatus.isTraining, jobId]);

  const checkTrainingStatus = async () => {
    if (!currentProject || !jobId) return;

    try {
      const response = await trainingApi.getStatus(currentProject.id, jobId);
      setTrainingStatus(response.data);

      // Get logs
      const logsResponse = await trainingApi.getLogs(currentProject.id, jobId);
      setLogs(logsResponse.data.logs || []);

      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setJobId(null);
      }
    } catch (error) {
      console.error('Failed to check training status:', error);
    }
  };

  const handleSearchModels = async () => {
    if (!modelSearch.trim()) return;

    try {
      const response = await huggingfaceApi.searchModels(modelSearch);
      setModelResults(response.data);
    } catch (error) {
      console.error('Failed to search models:', error);
    }
  };

  const handleStartTraining = async () => {
    if (!currentProject) {
      alert('Please select a project first');
      return;
    }

    if (!config.datasetId) {
      alert('Please select a dataset');
      return;
    }

    try {
      setTrainingStatus({
        isTraining: true,
        progress: 0,
        currentStep: 0,
        totalSteps: 0,
        loss: [],
        logs: [],
      });

      const response = await trainingApi.start(currentProject.id, config);
      setJobId(response.data.jobId);
    } catch (error) {
      console.error('Failed to start training:', error);
      alert('Failed to start training: ' + error.message);
      setTrainingStatus({ ...trainingStatus, isTraining: false });
    }
  };

  const handleStopTraining = async () => {
    if (!currentProject || !jobId) return;

    try {
      await trainingApi.stop(currentProject.id, jobId);
      setTrainingStatus({ ...trainingStatus, isTraining: false });
      setJobId(null);
    } catch (error) {
      console.error('Failed to stop training:', error);
    }
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <GraduationCap size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to start training</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Training Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Configure and monitor model fine-tuning with QLoRA
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Dataset Selection */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Dataset</h2>
            <select
              value={config.datasetId}
              onChange={(e) => setConfig({ ...config, datasetId: e.target.value })}
              className="input-field"
              disabled={trainingStatus.isTraining}
            >
              <option value="">Select a dataset...</option>
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.sample_count} samples)
                </option>
              ))}
            </select>
          </div>

          {/* Base Model Selection */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Base Model</h2>

            <div className="mb-4">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={modelSearch}
                  onChange={(e) => setModelSearch(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearchModels()}
                  className="input-field flex-1"
                  placeholder="Search HuggingFace models..."
                  disabled={trainingStatus.isTraining}
                />
                <button
                  onClick={handleSearchModels}
                  className="btn-secondary"
                  disabled={trainingStatus.isTraining}
                >
                  Search
                </button>
              </div>

              {modelResults.length > 0 && (
                <div className="mt-2 border border-gray-200 rounded-lg max-h-48 overflow-y-auto">
                  {modelResults.map((model) => (
                    <button
                      key={model.id}
                      onClick={() => {
                        setConfig({ ...config, baseModel: model.id });
                        setModelResults([]);
                      }}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-semibold text-gray-900">{model.id}</div>
                      {model.downloads && (
                        <div className="text-xs text-gray-500">
                          {model.downloads.toLocaleString()} downloads
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Selected Model
              </label>
              <input
                type="text"
                value={config.baseModel}
                onChange={(e) => setConfig({ ...config, baseModel: e.target.value })}
                className="input-field font-mono"
                placeholder="e.g., meta-llama/Llama-2-7b-hf"
                disabled={trainingStatus.isTraining}
              />
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Output Model Name
              </label>
              <input
                type="text"
                value={config.outputName}
                onChange={(e) => setConfig({ ...config, outputName: e.target.value })}
                className="input-field"
                placeholder="my-finetuned-model"
                disabled={trainingStatus.isTraining}
              />
            </div>
          </div>

          {/* Training Parameters */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Training Parameters</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Epochs
                </label>
                <input
                  type="number"
                  value={config.epochs}
                  onChange={(e) => setConfig({ ...config, epochs: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="100"
                  disabled={trainingStatus.isTraining}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Batch Size
                </label>
                <input
                  type="number"
                  value={config.batchSize}
                  onChange={(e) => setConfig({ ...config, batchSize: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="128"
                  disabled={trainingStatus.isTraining}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Learning Rate
                </label>
                <input
                  type="number"
                  value={config.learningRate}
                  onChange={(e) => setConfig({ ...config, learningRate: parseFloat(e.target.value) })}
                  className="input-field"
                  step="0.0001"
                  disabled={trainingStatus.isTraining}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Sequence Length
                </label>
                <input
                  type="number"
                  value={config.maxSeqLength}
                  onChange={(e) => setConfig({ ...config, maxSeqLength: parseInt(e.target.value) })}
                  className="input-field"
                  disabled={trainingStatus.isTraining}
                />
              </div>
            </div>
          </div>

          {/* QLoRA Parameters */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">QLoRA Parameters</h2>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LoRA Rank (r)
                </label>
                <input
                  type="number"
                  value={config.loraR}
                  onChange={(e) => setConfig({ ...config, loraR: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="256"
                  disabled={trainingStatus.isTraining}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LoRA Alpha
                </label>
                <input
                  type="number"
                  value={config.loraAlpha}
                  onChange={(e) => setConfig({ ...config, loraAlpha: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="256"
                  disabled={trainingStatus.isTraining}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  LoRA Dropout
                </label>
                <input
                  type="number"
                  value={config.loraDropout}
                  onChange={(e) => setConfig({ ...config, loraDropout: parseFloat(e.target.value) })}
                  className="input-field"
                  min="0"
                  max="1"
                  step="0.05"
                  disabled={trainingStatus.isTraining}
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Modules (comma-separated)
              </label>
              <input
                type="text"
                value={config.targetModules.join(', ')}
                onChange={(e) => setConfig({
                  ...config,
                  targetModules: e.target.value.split(',').map(m => m.trim()).filter(Boolean)
                })}
                className="input-field font-mono"
                placeholder="q_proj, v_proj, k_proj, o_proj"
                disabled={trainingStatus.isTraining}
              />
              <p className="text-sm text-gray-500 mt-1">
                Common modules: q_proj, v_proj, k_proj, o_proj, gate_proj, up_proj, down_proj
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            {!trainingStatus.isTraining ? (
              <button
                onClick={handleStartTraining}
                disabled={!config.datasetId}
                className="btn-primary flex items-center space-x-2 flex-1"
              >
                <Play size={20} />
                <span>Start Training</span>
              </button>
            ) : (
              <button
                onClick={handleStopTraining}
                className="btn-danger flex items-center space-x-2 flex-1"
              >
                <StopCircle size={20} />
                <span>Stop Training</span>
              </button>
            )}
          </div>
        </div>

        {/* Monitoring Panel */}
        <div className="space-y-6">
          {/* Progress */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress</h2>

            {trainingStatus.isTraining ? (
              <div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Training in progress...</span>
                    <span>{trainingStatus.currentStep} / {trainingStatus.totalSteps}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${trainingStatus.progress}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Loss:</span>
                    <span className="font-semibold">
                      {trainingStatus.loss[trainingStatus.loss.length - 1]?.value.toFixed(4) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Epoch:</span>
                    <span className="font-semibold">
                      {Math.floor((trainingStatus.currentStep / trainingStatus.totalSteps) * config.epochs) + 1} / {config.epochs}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Ready to train</p>
                <p className="text-sm mt-2">Configure settings and click Start</p>
              </div>
            )}
          </div>

          {/* Loss Chart */}
          {trainingStatus.loss && trainingStatus.loss.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <TrendingDown size={20} />
                <span>Training Loss</span>
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={trainingStatus.loss}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="step" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#0284c7" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Logs */}
          {logs.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Training Logs</h2>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-xs max-h-64 overflow-y-auto">
                {logs.map((log, idx) => (
                  <div key={idx} className="mb-1">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainingDashboard;
