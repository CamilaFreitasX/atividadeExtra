import json
import os
from datetime import datetime
from typing import Dict, List, Any

class MemorySystem:
    """Sistema de memória para armazenar análises e conclusões do agente"""
    
    def __init__(self, memory_file="agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()
        
    def load_memory(self) -> Dict:
        """Carrega memória do arquivo"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.initialize_memory()
        return self.initialize_memory()
    
    def initialize_memory(self) -> Dict:
        """Inicializa estrutura de memória"""
        return {
            "sessions": {},
            "global_insights": [],
            "dataset_analyses": {},
            "user_questions": [],
            "conclusions": []
        }
    
    def save_memory(self):
        """Salva memória no arquivo"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")
    
    def create_session(self, session_id: str, dataset_info: Dict):
        """Cria nova sessão de análise"""
        self.memory["sessions"][session_id] = {
            "created_at": datetime.now().isoformat(),
            "dataset_info": dataset_info,
            "questions_asked": [],
            "analyses_performed": [],
            "insights_generated": [],
            "visualizations_created": []
        }
        self.save_memory()
    
    def add_question(self, session_id: str, question: str, answer: str, analysis_type: str = None):
        """Adiciona pergunta e resposta à sessão"""
        if session_id not in self.memory["sessions"]:
            return False
        
        question_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "analysis_type": analysis_type
        }
        
        self.memory["sessions"][session_id]["questions_asked"].append(question_entry)
        self.memory["user_questions"].append(question_entry)
        self.save_memory()
        return True
    
    def add_analysis_result(self, session_id: str, analysis_type: str, results: Dict):
        """Adiciona resultado de análise à sessão"""
        if session_id not in self.memory["sessions"]:
            return False
        
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": analysis_type,
            "results": results
        }
        
        self.memory["sessions"][session_id]["analyses_performed"].append(analysis_entry)
        self.save_memory()
        return True
    
    def add_insight(self, session_id: str, insight: str, confidence: float = 0.8):
        """Adiciona insight gerado à sessão"""
        if session_id not in self.memory["sessions"]:
            return False
        
        insight_entry = {
            "timestamp": datetime.now().isoformat(),
            "insight": insight,
            "confidence": confidence
        }
        
        self.memory["sessions"][session_id]["insights_generated"].append(insight_entry)
        self.memory["global_insights"].append(insight_entry)
        self.save_memory()
        return True
    
    def add_conclusion(self, session_id: str, conclusion: str, supporting_evidence: List[str] = None):
        """Adiciona conclusão à sessão"""
        if session_id not in self.memory["sessions"]:
            return False
        
        conclusion_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "conclusion": conclusion,
            "supporting_evidence": supporting_evidence or []
        }
        
        self.memory["conclusions"].append(conclusion_entry)
        self.save_memory()
        return True
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Retorna resumo da sessão"""
        if session_id not in self.memory["sessions"]:
            return {}
        
        session = self.memory["sessions"][session_id]
        return {
            "dataset_info": session["dataset_info"],
            "total_questions": len(session["questions_asked"]),
            "total_analyses": len(session["analyses_performed"]),
            "total_insights": len(session["insights_generated"]),
            "recent_questions": session["questions_asked"][-5:],  # Últimas 5 perguntas
            "key_insights": session["insights_generated"][-3:]   # Últimos 3 insights
        }
    
    def get_relevant_context(self, current_question: str, session_id: str = None) -> str:
        """Retorna contexto relevante baseado na pergunta atual"""
        context_parts = []
        
        # Contexto da sessão atual
        if session_id and session_id in self.memory["sessions"]:
            session = self.memory["sessions"][session_id]
            
            # Perguntas similares anteriores
            similar_questions = []
            for q in session["questions_asked"][-10:]:  # Últimas 10 perguntas
                if any(word in q["question"].lower() for word in current_question.lower().split()):
                    similar_questions.append(q)
            
            if similar_questions:
                context_parts.append("Perguntas similares anteriores:")
                for q in similar_questions[-3:]:  # Últimas 3 similares
                    context_parts.append(f"- {q['question']}: {q['answer'][:200]}...")
            
            # Insights relevantes
            if session["insights_generated"]:
                context_parts.append("\\nInsights anteriores:")
                for insight in session["insights_generated"][-3:]:
                    context_parts.append(f"- {insight['insight']}")
        
        # Conclusões globais relevantes
        relevant_conclusions = []
        for conclusion in self.memory["conclusions"][-5:]:  # Últimas 5 conclusões
            if any(word in conclusion["conclusion"].lower() for word in current_question.lower().split()):
                relevant_conclusions.append(conclusion)
        
        if relevant_conclusions:
            context_parts.append("\\nConclusões relevantes de análises anteriores:")
            for conclusion in relevant_conclusions:
                context_parts.append(f"- {conclusion['conclusion']}")
        
        return "\\n".join(context_parts) if context_parts else ""
    
    def generate_session_conclusions(self, session_id: str) -> List[str]:
        """Gera conclusões baseadas na sessão atual"""
        if session_id not in self.memory["sessions"]:
            return []
        
        session = self.memory["sessions"][session_id]
        conclusions = []
        
        # Análise baseada nos insights gerados
        insights = session["insights_generated"]
        if len(insights) >= 3:
            conclusions.append(
                f"Baseado em {len(insights)} insights gerados, "
                f"os dados mostram padrões consistentes que sugerem "
                f"características específicas do dataset."
            )
        
        # Análise baseada nas perguntas feitas
        questions = session["questions_asked"]
        analysis_types = [q.get("analysis_type") for q in questions if q.get("analysis_type")]
        
        if "correlation" in analysis_types:
            conclusions.append(
                "A análise de correlações revelou relacionamentos importantes "
                "entre as variáveis do dataset."
            )
        
        if "outliers" in analysis_types:
            conclusions.append(
                "A detecção de outliers identificou pontos de dados atípicos "
                "que podem requerer investigação adicional."
            )
        
        if "distribution" in analysis_types:
            conclusions.append(
                "A análise de distribuições forneceu insights sobre "
                "a natureza e características das variáveis."
            )
        
        return conclusions
    
    def get_memory_stats(self) -> Dict:
        """Retorna estatísticas da memória"""
        return {
            "total_sessions": len(self.memory["sessions"]),
            "total_questions": len(self.memory["user_questions"]),
            "total_insights": len(self.memory["global_insights"]),
            "total_conclusions": len(self.memory["conclusions"]),
            "memory_file_size": os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0
        }
    
    def clear_session(self, session_id: str):
        """Limpa dados de uma sessão específica"""
        if session_id in self.memory["sessions"]:
            del self.memory["sessions"][session_id]
            self.save_memory()
    
    def clear_all_memory(self):
        """Limpa toda a memória"""
        self.memory = self.initialize_memory()
        self.save_memory()