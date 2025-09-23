import requests
from bs4 import BeautifulSoup
import time
import os

def analyze_seo(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        load_time = round(time.time() - start_time, 2)
        
        if response.status_code != 200:
            return {'URL': url, 'Error': f"Failed to fetch (status {response.status_code})"}

        soup = BeautifulSoup(response.text, 'lxml')

        # Meta title
        title = soup.title.string if soup.title else 'No title'
        title_suggestion = 'Good' if title and len(title) <= 60 else 'Too long or missing'

        # Meta description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag else 'No description'
        desc_suggestion = 'Good' if description and len(description) <= 160 else 'Too long or missing'

        # Headings
        headings = {f'H{h}': len(soup.find_all(f'h{h}')) for h in range(1, 4)}
        headings_suggestion = {f'H{h}': 'OK' if headings[f'H{h}']>0 else 'Missing' for h in range(1,4)}

        # Images
        images = soup.find_all('img')
        images_without_alt = len([img for img in images if not img.get('alt')])
        img_suggestion = 'All images have alt text' if images_without_alt==0 else f'{images_without_alt} missing alt'

        # Links
        links = soup.find_all('a')
        internal_links = len([link for link in links if link.get('href') and url in link.get('href')])
        external_links = len(links) - internal_links

        # SEO scoring
        score = 0
        score += 10 if title_suggestion=='Good' else 0
        score += 10 if desc_suggestion=='Good' else 0
        score += 10 if headings_suggestion['H1']=='OK' else 0
        score += 5 if headings_suggestion['H2']=='OK' else 0
        score += 5 if headings_suggestion['H3']=='OK' else 0
        score += 10 if images_without_alt==0 else 0
        score += 10 if load_time < 3 else 0
        score += 5 if internal_links>=5 else 0
        score += 5 if external_links>=5 else 0
        score = min(score, 100)

        return {
            'URL': url, 'Title': title, 'Title Suggestion': title_suggestion,
            'Description': description, 'Description Suggestion': desc_suggestion,
            'H1 Count': headings['H1'], 'H1 Suggestion': headings_suggestion['H1'],
            'H2 Count': headings['H2'], 'H2 Suggestion': headings_suggestion['H2'],
            'H3 Count': headings['H3'], 'H3 Suggestion': headings_suggestion['H3'],
            'Total Images': len(images), 'Images without Alt': images_without_alt,
            'Images Suggestion': img_suggestion, 'Internal Links': internal_links,
            'External Links': external_links, 'Page Load Time (s)': load_time,
            'Score': score
        }

    except Exception as e:
        return {'URL': url, 'Error': str(e), 'Score': 0}

def generate_html_report(report, filename):
    """Individual HTML report"""
    if 'Error' in report:
        content = f"<h1>{report['URL']}</h1><p style='color:red'>{report['Error']}</p>"
    else:
        content = f"""
        <h1>{report['URL']}</h1>
        <table border="1" cellpadding="5">
        <tr><th>Metric</th><th>Value</th><th>Suggestion</th></tr>
        <tr><td>Title</td><td>{report['Title']}</td><td>{report['Title Suggestion']}</td></tr>
        <tr><td>Description</td><td>{report['Description']}</td><td>{report['Description Suggestion']}</td></tr>
        <tr><td>H1 Count</td><td>{report['H1 Count']}</td><td>{report['H1 Suggestion']}</td></tr>
        <tr><td>H2 Count</td><td>{report['H2 Count']}</td><td>{report['H2 Suggestion']}</td></tr>
        <tr><td>H3 Count</td><td>{report['H3 Count']}</td><td>{report['H3 Suggestion']}</td></tr>
        <tr><td>Images without Alt</td><td>{report['Images without Alt']}</td><td>{report['Images Suggestion']}</td></tr>
        <tr><td>Page Load Time</td><td>{report['Page Load Time (s)']}</td><td>{'Good' if report['Page Load Time (s)']<3 else 'Slow'}</td></tr>
        <tr><td>Internal Links</td><td>{report['Internal Links']}</td><td>-</td></tr>
        <tr><td>External Links</td><td>{report['External Links']}</td><td>-</td></tr>
        <tr><td>SEO Score</td><td>{report['Score']}</td><td>-</td></tr>
        </table>
        """
    html = f"<html><body>{content}</body></html>"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_dashboard(all_reports, filename='reports/master_dashboard.html'):
    """Master HTML dashboard with sorted sites by Score ascending"""
    all_reports_sorted = sorted(all_reports, key=lambda x: x.get('Score',0))
    html_content = """
    <html><head><title>SEO Master Dashboard</title>
    <style>
    body { font-family: Arial; padding: 20px; }
    h1 { color: #4CAF50; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    .good { background-color: #c8e6c9; }
    .warning { background-color: #fff9c4; }
    .error { background-color: #f8d7da; color: #721c24; }
    </style></head><body>
    <h1>SEO Master Dashboard (Worst to Best)</h1>
    <table>
    <tr><th>Website</th><th>Title</th><th>Description</th><th>H1</th><th>H2</th><th>H3</th>
    <th>Images Alt</th><th>Page Load</th><th>Score</th></tr>
    """
    for r in all_reports_sorted:
        if 'Error' in r:
            html_content += f"<tr class='error'><td>{r['URL']}</td><td colspan='8'>{r['Error']}</td></tr>"
        else:
            html_content += f"""
            <tr>
                <td>{r['URL']}</td>
                <td class='{'good' if r['Title Suggestion']=='Good' else 'warning'}'>{r['Title']}</td>
                <td class='{'good' if r['Description Suggestion']=='Good' else 'warning'}'>{r['Description']}</td>
                <td class='{'good' if r['H1 Suggestion']=='OK' else 'warning'}'>{r['H1 Count']}</td>
                <td class='{'good' if r['H2 Suggestion']=='OK' else 'warning'}'>{r['H2 Count']}</td>
                <td class='{'good' if r['H3 Suggestion']=='OK' else 'warning'}'>{r['H3 Count']}</td>
                <td class='{'good' if r['Images without Alt']==0 else 'warning'}'>{r['Images without Alt']}</td>
                <td class='{'good' if r['Page Load Time (s)']<3 else 'warning'}'>{r['Page Load Time (s)']}</td>
                <td>{r['Score']}</td>
            </tr>
            """
    html_content += "</table></body></html>"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Master dashboard saved: {os.path.abspath(filename)}")

def batch_analyze(url_list):
    if not os.path.exists('reports'):
        os.mkdir('reports')
    all_reports = []
    for url in url_list:
        report = analyze_seo(url)
        all_reports.append(report)
        safe_name = url.replace('https://','').replace('http://','').replace('/','_')
        generate_html_report(report, f'reports/{safe_name}_report.html')
    generate_dashboard(all_reports)

if __name__ == "__main__":
    urls = input("Enter website URLs separated by comma: ").split(',')
    urls = [u.strip() for u in urls]
    batch_analyze(urls)
