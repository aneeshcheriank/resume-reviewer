from langchain_community.tools import DuckDuckGoSearchResults

search_tool = DuckDuckGoSearchResults(max_results=3)

project_research_tool_list = [search_tool]
project_research_tool_mapping = {tool.name: tool for tool in project_research_tool_list}