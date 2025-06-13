# AI Product Manager - Multi-Agent System

A sophisticated multi-agent system built with CrewAI and Flask that provides comprehensive project analysis and planning capabilities.

## Features

- Multi-agent system with specialized roles (Product Manager, Developer, QA, etc.)
- Real-time project analysis and recommendations
- Interactive web interface with live updates
- Comprehensive project planning and risk assessment

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

4. Run the application:
```bash
flask run
```

## Project Structure

```
ai_product_manager/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│   └── agents/
├── config.py
├── requirements.txt
└── run.py
```

## Contributing

This project is under active development. Please refer to the documentation for contribution guidelines.

## License

MIT License 