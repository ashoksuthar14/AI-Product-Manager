import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        # Load keys from environment
        keys_env = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
        self.working_api_keys = [key.strip() for key in keys_env.split(",") if key.strip()]
        
        if not self.working_api_keys:
            print("\u26a0\ufe0f No GEMINI_API_KEY(S) configured. LLM features will be unavailable until keys are set.")
        
        # Assign keys to agents (reuse as needed)
        def key_at(index: int):
            if not self.working_api_keys:
                return None
            return self.working_api_keys[min(index, len(self.working_api_keys) - 1)]
        
        self.agent_api_keys = {
            'product_manager': key_at(0),
            'developer': key_at(1),
            'qa': key_at(2),
            'ai_engineer': key_at(3),
            'pm_final': key_at(0)
        }
        
        # Initialize Gemini models for each agent
        self.agent_models = {}
        for agent, api_key in self.agent_api_keys.items():
            if not api_key:
                continue
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                self.agent_models[agent] = (api_key, model)
                print(f"\u2705 Initialized {agent} with Gemini key {api_key[:10]}...")
            except Exception as e:
                print(f"\u274c Failed to initialize {agent} with key {api_key[:10]}...: {e}")

    async def get_agent_response(self, agent_type: str, prompt: str, system_prompt: str = None) -> str:
        """Get response from specific agent's assigned Gemini API key."""
        
        agent_key_map = {
            'product_manager': 'product_manager',
            'developer': 'developer', 
            'qa': 'qa',
            'ai_engineer': 'ai_engineer',
            'pm_final': 'pm_final'
        }
        
        agent_key = agent_key_map.get(agent_type, 'product_manager')
        
        if agent_key not in self.agent_models:
            raise RuntimeError(
                f"No API key assigned for agent: {agent_type}. Set GEMINI_API_KEY or GEMINI_API_KEYS in the environment."
            )
        
        api_key, model = self.agent_models[agent_key]
        
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            print(f"\ud83c\udfaf {agent_type} using Gemini key {api_key[:10]}...")
            response = model.generate_content(full_prompt)
            print(f"\u2705 {agent_type} response received successfully")
            return response.text
        except Exception as e:
            print(f"\u274c {agent_type} failed with key {api_key[:10]}...: {str(e)}")
            
            # Try fallback with a different key if available
            fallback_keys = [key for key in self.working_api_keys if key != api_key]
            if fallback_keys:
                print(f"\ud83d\udd04 Trying fallback key for {agent_type}...")
                try:
                    fallback_key = fallback_keys[0]
                    genai.configure(api_key=fallback_key)
                    fallback_model = genai.GenerativeModel('gemini-2.0-flash')
                    fallback_response = fallback_model.generate_content(full_prompt)
                    print(f"\u2705 {agent_type} succeeded with fallback key {fallback_key[:10]}...")
                    return fallback_response.text
                except Exception as fallback_error:
                    print(f"\u274c Fallback also failed for {agent_type}: {str(fallback_error)}")
            
            raise e

    async def get_gemini_response(self, prompt: str, system_prompt: str = None) -> str:
        """Fallback method - uses product manager's key."""
        return await self.get_agent_response('product_manager', prompt, system_prompt)

    async def get_fallback_response(self, prompt: str, system_prompt: str = None) -> str:
        """Use product manager's key as fallback."""
        return await self.get_agent_response('product_manager', prompt, system_prompt)

    def get_api_status(self) -> dict:
        """Get current status of all assigned APIs."""
        status = {}
        for agent, value in self.agent_models.items():
            api_key = value[0]
            status[agent] = f"Key {api_key[:10]}... \u2705"
        return status