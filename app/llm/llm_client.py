import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        # Working Gemini API keys (removed the expired one)
        self.working_api_keys = [
            "AIzaSyCccRqU5_E2lmAbXzIXIb_pMhlXgnyePMk",
            "AIzaSyCcka9PdfHELRaOSgWsirfIenUOxye3Lk4",
            "AIzaSyCkvWRXLcr85HFflDPizh4TCB-U9h__O1U",
            "AIzaSyA0OrH3aWcCr5f6ggv5orRsaB01IOXjCm0"
        ]
        
        # Assign working keys to agents
        self.agent_api_keys = {
            'product_manager': self.working_api_keys[0],  # AIzaSyCccRqU5_E2lmAbXzIXIb_pMhlXgnyePMk
            'developer': self.working_api_keys[1],        # AIzaSyCcka9PdfHELRaOSgWsirfIenUOxye3Lk4
            'qa': self.working_api_keys[2],               # AIzaSyCkvWRXLcr85HFflDPizh4TCB-U9h__O1U
            'ai_engineer': self.working_api_keys[3],      # AIzaSyA0OrH3aWcCr5f6ggv5orRsaB01IOXjCm0
            'pm_final': self.working_api_keys[0]          # Reuse first key for PM final
        }
        
        # Initialize Gemini models for each agent
        self.agent_models = {}
        for agent, api_key in self.agent_api_keys.items():
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                self.agent_models[agent] = (api_key, model)
                print(f"✅ Initialized {agent} with Gemini key {api_key[:10]}...")
            except Exception as e:
                print(f"❌ Failed to initialize {agent} with key {api_key[:10]}...: {e}")

    async def get_agent_response(self, agent_type: str, prompt: str, system_prompt: str = None) -> str:
        """Get response from specific agent's assigned Gemini API key."""
        
        # Map agent types to keys
        agent_key_map = {
            'product_manager': 'product_manager',
            'developer': 'developer', 
            'qa': 'qa',
            'ai_engineer': 'ai_engineer',
            'pm_final': 'pm_final'
        }
        
        agent_key = agent_key_map.get(agent_type, 'product_manager')
        
        if agent_key not in self.agent_models:
            raise RuntimeError(f"No API key assigned for agent: {agent_type}")
        
        api_key, model = self.agent_models[agent_key]
        
        try:
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            print(f"🎯 {agent_type} using Gemini key {api_key[:10]}...")
            response = model.generate_content(full_prompt)
            print(f"✅ {agent_type} response received successfully")
            return response.text
        except Exception as e:
            print(f"❌ {agent_type} failed with key {api_key[:10]}...: {str(e)}")
            
            # Try fallback with a different key if available
            fallback_keys = [key for key in self.working_api_keys if key != api_key]
            if fallback_keys:
                print(f"🔄 Trying fallback key for {agent_type}...")
                try:
                    fallback_key = fallback_keys[0]
                    genai.configure(api_key=fallback_key)
                    fallback_model = genai.GenerativeModel('gemini-2.0-flash')
                    fallback_response = fallback_model.generate_content(full_prompt)
                    print(f"✅ {agent_type} succeeded with fallback key {fallback_key[:10]}...")
                    return fallback_response.text
                except Exception as fallback_error:
                    print(f"❌ Fallback also failed for {agent_type}: {str(fallback_error)}")
            
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
        for agent, (api_key, _) in self.agent_models.items():
            status[agent] = f"Key {api_key[:10]}... ✅"
        return status