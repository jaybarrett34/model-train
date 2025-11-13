import { create } from 'zustand';

const useStore = create((set, get) => ({
  // Current project
  currentProject: null,
  setCurrentProject: (project) => set({ currentProject: project }),

  // XML Pattern State
  xmlPattern: {
    tags: [],
    rootTag: null,
  },
  setXmlPattern: (pattern) => set({ xmlPattern: pattern }),
  addTag: (tag) => set((state) => ({
    xmlPattern: {
      ...state.xmlPattern,
      tags: [...state.xmlPattern.tags, tag],
    },
  })),
  updateTag: (tagId, updates) => set((state) => ({
    xmlPattern: {
      ...state.xmlPattern,
      tags: state.xmlPattern.tags.map((tag) =>
        tag.id === tagId ? { ...tag, ...updates } : tag
      ),
    },
  })),
  removeTag: (tagId) => set((state) => ({
    xmlPattern: {
      ...state.xmlPattern,
      tags: state.xmlPattern.tags.filter((tag) => tag.id !== tagId),
    },
  })),

  // Training State
  trainingStatus: {
    isTraining: false,
    progress: 0,
    currentStep: 0,
    totalSteps: 0,
    loss: [],
    logs: [],
  },
  setTrainingStatus: (status) => set({ trainingStatus: status }),
  updateTrainingProgress: (progress) => set((state) => ({
    trainingStatus: {
      ...state.trainingStatus,
      ...progress,
    },
  })),

  // Generation State
  generationStatus: {
    isGenerating: false,
    progress: 0,
    currentSample: 0,
    totalSamples: 0,
    generatedData: [],
  },
  setGenerationStatus: (status) => set({ generationStatus: status }),
  updateGenerationProgress: (progress) => set((state) => ({
    generationStatus: {
      ...state.generationStatus,
      ...progress,
    },
  })),

  // Projects list
  projects: [],
  setProjects: (projects) => set({ projects }),
  addProject: (project) => set((state) => ({
    projects: [...state.projects, project],
  })),
  deleteProject: (projectId) => set((state) => ({
    projects: state.projects.filter((p) => p.id !== projectId),
  })),

  // Datasets
  datasets: [],
  setDatasets: (datasets) => set({ datasets }),
  addDataset: (dataset) => set((state) => ({
    datasets: [...state.datasets, dataset],
  })),

  // Models
  models: [],
  setModels: (models) => set({ models }),
  addModel: (model) => set((state) => ({
    models: [...state.models, model],
  })),
}));

export default useStore;
