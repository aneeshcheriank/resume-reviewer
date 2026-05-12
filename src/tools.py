from langchain_community.tools import DuckDuckGoSearchResult

search_tool = DuckDuckGoSearchResult(max_results=3)

project_research_tool_list = [search_tool]
project_research_tool_mapping = {tool.name: tool for tool in project_research_tool_list}