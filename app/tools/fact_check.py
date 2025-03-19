"""
Fact Check tool using Google Fact Check API.
"""

import requests


# Function to format the fact-checked claims in a readable way
def format_claims(response):
    claims = response.get('claims', [])
    result = ""
    for i, claim in enumerate(claims, start=1):
        result += f"#### **Claim {i}**\n"
        result += f'"{claim.get("text", "No text available")}"\n'
        
        # Check if 'claimant' exists in the claim
        claimant = claim.get('claimant', 'Unknown claimant')
        result += f"- **Claimant:** {claimant}\n"
        
        # Check if 'claimDate' exists in the claim
        claim_date = claim.get('claimDate', 'Unknown date')
        result += f"- **Claim Date:** {claim_date}\n"
        
        # Loop through the reviews
        for review in claim.get("claimReview", []):
            publisher = review["publisher"]["name"]
            title = review["title"]
            url = review["url"]
            rating = review["textualRating"]
            
            result += f"- **Fact Check:** *{rating}*\n"
            result += f"- **Source:** [{title}]({url})\n"
        
        result += "\n---"
    return result

def fact_check(query: str) -> dict[str, str]:
    """
    You need to use this tool for fact checks. Retrieves fact-check results from Google's Fact Check Tools API.
    
    Args:
        query: Search query string related to the fact-check topic.
    
    Returns:
        A dictionary containing the fact-check results.
    """
    API_KEY = "AIzaSyAX4YaVdXc0W5ESAgTlAvNXLa4GafbglpU"
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={API_KEY}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return {"output": format_claims(response.json())}
    else:
        return {"error": f"Error {response.status_code}: {response.text}"}