import { useState, useEffect } from 'react';
import { Calculator, TrendingUp, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import useStore from '../store/useStore';
import api from '../services/api';

const SizeAnalyzer = () => {
  const { currentProject, xmlPattern } = useStore();
  const [analysis, setAnalysis] = useState(null);
  const [config, setConfig] = useState({
    targetModel: 'llama-2-7b',
    taskComplexity: 'medium',
    desiredAccuracy: 0.85,
    availableVRAM: 16,
    trainingTime: 'moderate',
  });
  const [calculating, setCalculating] = useState(false);

  const complexityLevels = {
    simple: { label: 'Simple', description: 'Basic classification, simple QA', multiplier: 1 },
    medium: { label: 'Medium', description: 'Multi-turn dialogue, structured generation', multiplier: 2 },
    complex: { label: 'Complex', description: 'Code generation, reasoning tasks', multiplier: 4 },
    expert: { label: 'Expert', description: 'Domain-specific, highly specialized', multiplier: 8 },
  };

  const modelSpecs = {
    'llama-2-7b': { params: '7B', minSamples: 100, recommendedSamples: 500 },
    'llama-2-13b': { params: '13B', minSamples: 200, recommendedSamples: 1000 },
    'mistral-7b': { params: '7B', minSamples: 100, recommendedSamples: 500 },
    'mixtral-8x7b': { params: '47B', minSamples: 300, recommendedSamples: 1500 },
    'phi-2': { params: '2.7B', minSamples: 50, recommendedSamples: 300 },
  };

  const calculateDatasetSize = async () => {
    setCalculating(true);

    try {
      // If backend has an analyzer endpoint
      const response = await api.post('/analyze/dataset-size', {
        projectId: currentProject?.id,
        pattern: xmlPattern,
        config,
      });
      setAnalysis(response.data);
    } catch (error) {
      console.error('API not available, using client-side calculation');

      // Fallback to client-side calculation
      const baseMultiplier = complexityLevels[config.taskComplexity].multiplier;
      const modelSpec = modelSpecs[config.targetModel];
      const accuracyMultiplier = config.desiredAccuracy <= 0.75 ? 0.5 : config.desiredAccuracy <= 0.85 ? 1 : 1.5;

      const minSamples = Math.ceil(modelSpec.minSamples * baseMultiplier * accuracyMultiplier);
      const recommendedSamples = Math.ceil(modelSpec.recommendedSamples * baseMultiplier * accuracyMultiplier);
      const optimalSamples = Math.ceil(recommendedSamples * 1.5);

      // Calculate training estimates
      const samplesPerHour = config.availableVRAM >= 24 ? 200 : config.availableVRAM >= 16 ? 150 : 100;
      const estimatedHours = recommendedSamples / samplesPerHour;

      setAnalysis({
        recommendations: {
          minimum: minSamples,
          recommended: recommendedSamples,
          optimal: optimalSamples,
        },
        breakdown: {
          baseRequirement: modelSpec.minSamples,
          complexityMultiplier: baseMultiplier,
          accuracyMultiplier: accuracyMultiplier,
          finalCalculation: recommendedSamples,
        },
        trainingEstimates: {
          samplesPerHour,
          estimatedHours: estimatedHours.toFixed(1),
          estimatedCost: (estimatedHours * 2.5).toFixed(2), // ~$2.50/hr for GPU
        },
        qualityMetrics: {
          expectedAccuracy: config.desiredAccuracy,
          confidenceLevel: minSamples < 200 ? 'low' : recommendedSamples < 500 ? 'medium' : 'high',
          overfit_risk: minSamples < 100 ? 'high' : minSamples < 300 ? 'medium' : 'low',
        },
        comparisonData: [
          { name: 'Minimum', samples: minSamples, cost: (minSamples / samplesPerHour * 2.5).toFixed(2) },
          { name: 'Recommended', samples: recommendedSamples, cost: (recommendedSamples / samplesPerHour * 2.5).toFixed(2) },
          { name: 'Optimal', samples: optimalSamples, cost: (optimalSamples / samplesPerHour * 2.5).toFixed(2) },
        ],
      });
    } finally {
      setCalculating(false);
    }
  };

  useEffect(() => {
    if (currentProject) {
      calculateDatasetSize();
    }
  }, [currentProject]);

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Calculator size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to analyze dataset requirements</p>
        </div>
      </div>
    );
  }

  const COLORS = ['#0ea5e9', '#0284c7', '#0369a1'];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dataset Size Analyzer</h1>
        <p className="text-gray-600 mt-2">
          Calculate optimal dataset size requirements for your training task
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Model
                </label>
                <select
                  value={config.targetModel}
                  onChange={(e) => setConfig({ ...config, targetModel: e.target.value })}
                  className="input-field"
                >
                  {Object.entries(modelSpecs).map(([key, spec]) => (
                    <option key={key} value={key}>
                      {key} ({spec.params})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Task Complexity
                </label>
                <select
                  value={config.taskComplexity}
                  onChange={(e) => setConfig({ ...config, taskComplexity: e.target.value })}
                  className="input-field"
                >
                  {Object.entries(complexityLevels).map(([key, level]) => (
                    <option key={key} value={key}>
                      {level.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  {complexityLevels[config.taskComplexity].description}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Desired Accuracy
                </label>
                <input
                  type="range"
                  min="0.7"
                  max="0.95"
                  step="0.05"
                  value={config.desiredAccuracy}
                  onChange={(e) => setConfig({ ...config, desiredAccuracy: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>70%</span>
                  <span className="font-semibold text-primary-600">
                    {(config.desiredAccuracy * 100).toFixed(0)}%
                  </span>
                  <span>95%</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Available VRAM (GB)
                </label>
                <select
                  value={config.availableVRAM}
                  onChange={(e) => setConfig({ ...config, availableVRAM: parseInt(e.target.value) })}
                  className="input-field"
                >
                  <option value="8">8 GB</option>
                  <option value="12">12 GB</option>
                  <option value="16">16 GB</option>
                  <option value="24">24 GB</option>
                  <option value="40">40 GB (A100)</option>
                  <option value="80">80 GB (H100)</option>
                </select>
              </div>

              <button
                onClick={calculateDatasetSize}
                disabled={calculating}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                <Calculator size={20} />
                <span>{calculating ? 'Calculating...' : 'Recalculate'}</span>
              </button>
            </div>
          </div>

          {/* Model Info */}
          {config.targetModel && (
            <div className="card bg-blue-50 border-2 border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-3 flex items-center space-x-2">
                <Info size={18} />
                <span>Model Information</span>
              </h3>
              <div className="text-sm text-blue-800 space-y-2">
                <div className="flex justify-between">
                  <span>Parameters:</span>
                  <span className="font-semibold">{modelSpecs[config.targetModel].params}</span>
                </div>
                <div className="flex justify-between">
                  <span>Min Samples:</span>
                  <span className="font-semibold">{modelSpecs[config.targetModel].minSamples}</span>
                </div>
                <div className="flex justify-between">
                  <span>Recommended:</span>
                  <span className="font-semibold">{modelSpecs[config.targetModel].recommendedSamples}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {analysis ? (
            <>
              {/* Recommendations */}
              <div className="grid grid-cols-3 gap-4">
                <div className="card border-2 border-yellow-200 bg-yellow-50">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertCircle size={20} className="text-yellow-600" />
                    <h3 className="font-semibold text-gray-900">Minimum</h3>
                  </div>
                  <div className="text-3xl font-bold text-yellow-600 mb-1">
                    {analysis.recommendations.minimum}
                  </div>
                  <p className="text-sm text-gray-600">samples needed</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Basic functionality, may underfit
                  </p>
                </div>

                <div className="card border-2 border-green-200 bg-green-50">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle size={20} className="text-green-600" />
                    <h3 className="font-semibold text-gray-900">Recommended</h3>
                  </div>
                  <div className="text-3xl font-bold text-green-600 mb-1">
                    {analysis.recommendations.recommended}
                  </div>
                  <p className="text-sm text-gray-600">samples needed</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Good balance of quality and cost
                  </p>
                </div>

                <div className="card border-2 border-blue-200 bg-blue-50">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp size={20} className="text-blue-600" />
                    <h3 className="font-semibold text-gray-900">Optimal</h3>
                  </div>
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    {analysis.recommendations.optimal}
                  </div>
                  <p className="text-sm text-gray-600">samples needed</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Best quality, higher cost
                  </p>
                </div>
              </div>

              {/* Comparison Chart */}
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Size Comparison</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analysis.comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis yAxisId="left" orientation="left" stroke="#0284c7" />
                    <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="samples" fill="#0284c7" name="Samples" />
                    <Bar yAxisId="right" dataKey="cost" fill="#10b981" name="Est. Cost ($)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Training Estimates */}
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Training Estimates</h2>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Throughput</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {analysis.trainingEstimates.samplesPerHour}
                    </div>
                    <div className="text-xs text-gray-500">samples/hour</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Time Required</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {analysis.trainingEstimates.estimatedHours}
                    </div>
                    <div className="text-xs text-gray-500">hours</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Estimated Cost</div>
                    <div className="text-2xl font-bold text-gray-900">
                      ${analysis.trainingEstimates.estimatedCost}
                    </div>
                    <div className="text-xs text-gray-500">GPU time</div>
                  </div>
                </div>
              </div>

              {/* Quality Metrics */}
              <div className="card">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Quality Assessment</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Expected Accuracy</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-48 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${analysis.qualityMetrics.expectedAccuracy * 100}%` }}
                        />
                      </div>
                      <span className="font-semibold text-gray-900 w-12">
                        {(analysis.qualityMetrics.expectedAccuracy * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Confidence Level</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      analysis.qualityMetrics.confidenceLevel === 'high' ? 'bg-green-100 text-green-800' :
                      analysis.qualityMetrics.confidenceLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {analysis.qualityMetrics.confidenceLevel.toUpperCase()}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Overfitting Risk</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      analysis.qualityMetrics.overfit_risk === 'low' ? 'bg-green-100 text-green-800' :
                      analysis.qualityMetrics.overfit_risk === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {analysis.qualityMetrics.overfit_risk.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Calculation Breakdown */}
              <div className="card bg-gray-50">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Calculation Details</h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Base requirement:</span>
                    <span className="font-mono">{analysis.breakdown.baseRequirement} samples</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Complexity multiplier:</span>
                    <span className="font-mono">× {analysis.breakdown.complexityMultiplier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Accuracy multiplier:</span>
                    <span className="font-mono">× {analysis.breakdown.accuracyMultiplier.toFixed(1)}</span>
                  </div>
                  <div className="border-t border-gray-300 pt-2 mt-2 flex justify-between font-semibold">
                    <span className="text-gray-900">Final recommendation:</span>
                    <span className="font-mono text-primary-600">{analysis.breakdown.finalCalculation} samples</span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="card text-center py-12">
              <Calculator size={48} className="mx-auto text-gray-400 mb-4 animate-pulse" />
              <p className="text-gray-600">Calculating dataset requirements...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SizeAnalyzer;
