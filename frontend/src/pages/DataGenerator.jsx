import { useState, useEffect } from 'react';
import { Play, StopCircle, RefreshCw, Eye } from 'lucide-react';
import { generationApi } from '../services/api';
import useStore from '../store/useStore';

const DataGenerator = () => {
  const { currentProject, generationStatus, setGenerationStatus } = useStore();
  const [config, setConfig] = useState({
    objective: '',
    numSamples: 100,
    provider: 'ollama',
    model: 'llama2',
    mode: 'patterned',
    temperature: 0.7,
    apiUrl: 'http://localhost:11434',
    apiKey: '',
  });
  const [jobId, setJobId] = useState(null);
  const [generatedSamples, setGeneratedSamples] = useState([]);
  const [previewSample, setPreviewSample] = useState(null);

  useEffect(() => {
    let interval;
    if (generationStatus.isGenerating && jobId) {
      interval = setInterval(checkGenerationStatus, 2000);
    }
    return () => clearInterval(interval);
  }, [generationStatus.isGenerating, jobId]);

  const checkGenerationStatus = async () => {
    if (!currentProject || !jobId) return;

    try {
      const response = await generationApi.getStatus(currentProject.id, jobId);
      setGenerationStatus(response.data);

      if (response.data.status === 'completed') {
        setGeneratedSamples(response.data.samples || []);
        setJobId(null);
      }
    } catch (error) {
      console.error('Failed to check generation status:', error);
    }
  };

  const handleStartGeneration = async () => {
    if (!currentProject) {
      alert('Please select a project first');
      return;
    }

    if (!config.objective.trim()) {
      alert('Please provide an objective/task description');
      return;
    }

    try {
      setGenerationStatus({
        isGenerating: true,
        progress: 0,
        currentSample: 0,
        totalSamples: config.numSamples,
        generatedData: [],
      });

      const response = await generationApi.generate(currentProject.id, config);
      setJobId(response.data.jobId);
    } catch (error) {
      console.error('Failed to start generation:', error);
      alert('Failed to start generation: ' + error.message);
      setGenerationStatus({ ...generationStatus, isGenerating: false });
    }
  };

  const handleStopGeneration = async () => {
    if (!currentProject || !jobId) return;

    try {
      await generationApi.cancel(currentProject.id, jobId);
      setGenerationStatus({ ...generationStatus, isGenerating: false });
      setJobId(null);
    } catch (error) {
      console.error('Failed to stop generation:', error);
    }
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <RefreshCw size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to generate data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Data Generator</h1>
        <p className="text-gray-600 mt-2">
          Generate synthetic training data using AI
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Objective */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Objective</h2>
            <textarea
              value={config.objective}
              onChange={(e) => setConfig({ ...config, objective: e.target.value })}
              className="input-field"
              rows="4"
              placeholder="Describe the task or objective for the AI model. E.g., 'Generate product descriptions for an e-commerce site' or 'Create customer support responses'"
              disabled={generationStatus.isGenerating}
            />
          </div>

          {/* AI Provider Configuration */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Provider</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider
                </label>
                <select
                  value={config.provider}
                  onChange={(e) => setConfig({ ...config, provider: e.target.value })}
                  className="input-field"
                  disabled={generationStatus.isGenerating}
                >
                  <option value="ollama">Ollama (Local)</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="custom">Custom API</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <input
                  type="text"
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  className="input-field"
                  placeholder="llama2, gpt-4, claude-3-opus, etc."
                  disabled={generationStatus.isGenerating}
                />
              </div>
            </div>

            {config.provider !== 'ollama' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={config.apiKey}
                  onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                  className="input-field"
                  placeholder="Enter your API key"
                  disabled={generationStatus.isGenerating}
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API URL
              </label>
              <input
                type="text"
                value={config.apiUrl}
                onChange={(e) => setConfig({ ...config, apiUrl: e.target.value })}
                className="input-field"
                placeholder="http://localhost:11434"
                disabled={generationStatus.isGenerating}
              />
            </div>
          </div>

          {/* Generation Settings */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Generation Settings</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Samples
                </label>
                <input
                  type="number"
                  value={config.numSamples}
                  onChange={(e) => setConfig({ ...config, numSamples: parseInt(e.target.value) })}
                  className="input-field"
                  min="1"
                  max="10000"
                  disabled={generationStatus.isGenerating}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature
                </label>
                <input
                  type="number"
                  value={config.temperature}
                  onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                  className="input-field"
                  min="0"
                  max="2"
                  step="0.1"
                  disabled={generationStatus.isGenerating}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Generation Mode
              </label>
              <select
                value={config.mode}
                onChange={(e) => setConfig({ ...config, mode: e.target.value })}
                className="input-field"
                disabled={generationStatus.isGenerating}
              >
                <option value="pseudorandom">Pseudorandom - Random variations</option>
                <option value="patterned">Patterned - Follow XML pattern</option>
                <option value="forced">Forced - Strict pattern adherence</option>
              </select>
              <p className="text-sm text-gray-500 mt-2">
                {config.mode === 'pseudorandom' && 'Generate random variations without strict pattern enforcement'}
                {config.mode === 'patterned' && 'Generate data following the XML pattern with some flexibility'}
                {config.mode === 'forced' && 'Strictly enforce all pattern constraints and structure'}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            {!generationStatus.isGenerating ? (
              <button
                onClick={handleStartGeneration}
                className="btn-primary flex items-center space-x-2 flex-1"
              >
                <Play size={20} />
                <span>Start Generation</span>
              </button>
            ) : (
              <button
                onClick={handleStopGeneration}
                className="btn-danger flex items-center space-x-2 flex-1"
              >
                <StopCircle size={20} />
                <span>Stop Generation</span>
              </button>
            )}
          </div>
        </div>

        {/* Status Panel */}
        <div className="space-y-6">
          {/* Progress */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress</h2>

            {generationStatus.isGenerating ? (
              <div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Generating samples...</span>
                    <span>{generationStatus.currentSample} / {generationStatus.totalSamples}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${generationStatus.progress}%` }}
                    />
                  </div>
                </div>

                <div className="animate-pulse flex space-x-2 items-center text-primary-600">
                  <RefreshCw size={20} className="animate-spin" />
                  <span className="text-sm">Processing...</span>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Ready to generate data</p>
                <p className="text-sm mt-2">Configure settings and click Start</p>
              </div>
            )}
          </div>

          {/* Generated Samples Preview */}
          {generatedSamples.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Generated Samples ({generatedSamples.length})
              </h2>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {generatedSamples.slice(0, 10).map((sample, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 border border-gray-200 rounded-lg hover:border-primary-400 cursor-pointer transition-colors"
                    onClick={() => setPreviewSample(sample)}
                  >
                    <div className="text-sm font-mono text-gray-700 truncate">
                      {JSON.stringify(sample).substring(0, 100)}...
                    </div>
                  </div>
                ))}
              </div>

              {generatedSamples.length > 10 && (
                <p className="text-sm text-gray-500 mt-3 text-center">
                  Showing 10 of {generatedSamples.length} samples
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {previewSample && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setPreviewSample(null)}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Sample Preview</h3>
              <button
                onClick={() => setPreviewSample(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>
            <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto">
              {JSON.stringify(previewSample, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataGenerator;
