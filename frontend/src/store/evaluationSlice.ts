import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Evaluation {
  id: string;
  company_name: string;
  sector: string;
  stage: string;
  status: string;
  progress?: number;
  overall_score?: number;
  risk_level?: string;
  recommendation?: string;
  created_at: string;
  updated_at: string;
}

interface EvaluationState {
  evaluations: Evaluation[];
  currentEvaluation: Evaluation | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: EvaluationState = {
  evaluations: [],
  currentEvaluation: null,
  isLoading: false,
  error: null,
};

const evaluationSlice = createSlice({
  name: 'evaluation',
  initialState,
  reducers: {
    setEvaluations: (state, action: PayloadAction<Evaluation[]>) => {
      state.evaluations = action.payload;
      state.isLoading = false;
      state.error = null;
    },
    setCurrentEvaluation: (state, action: PayloadAction<Evaluation>) => {
      state.currentEvaluation = action.payload;
    },
    addEvaluation: (state, action: PayloadAction<Evaluation>) => {
      state.evaluations.unshift(action.payload);
    },
    updateEvaluation: (state, action: PayloadAction<Evaluation>) => {
      const index = state.evaluations.findIndex(e => e.id === action.payload.id);
      if (index !== -1) {
        state.evaluations[index] = action.payload;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
  },
});

export const {
  setEvaluations,
  setCurrentEvaluation,
  addEvaluation,
  updateEvaluation,
  setLoading,
  setError,
} = evaluationSlice.actions;

export default evaluationSlice.reducer;