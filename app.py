import asyncio
from flask import Flask,jsonify,request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from mcp_agent import setup_team
from pyngrok import ngrok

load_dotenv()
# Load environment variables
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')



# Set the port for the Flask app
port = 7001
app = Flask(__name__)
CORS(app)


async def run_task(task:str)->str:
    team = await setup_team()
    output=[]
    async for msg in team.run_stream(task=task):
        output.append(str(msg))

    return '\n \n \n'.join(output)




#====================================================================================================



@app.route('/health',methods=['GET'])
def health():
    return jsonify({"status":'ok','message':'Notion MCP Flask App is live'}),200


@app.route('/',methods=['GET'])
def root():
    return jsonify({'message':' MCP Notion app is live, use /health or /run to work '}),200


@app.route('/run',methods=['POST'])
def run():
    try:
        data = request.get_json()

        task = data.get('task')

        if not task:
            return jsonify ({'error':'Missing Task'}), 400
        
        print(f'Got the task {task}')

        result = asyncio.run(run_task(task))

        return jsonify({'status':'sucess','result':result}),200
        
    except Exception as e:
        return jsonify({'status':'error','result':str(e)}),500


if __name__=='__main__':
    
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    public_url = ngrok.connect(port)
    print(f"Public URL:{public_url}/api/hello \n \n")


    app.run(port = port)