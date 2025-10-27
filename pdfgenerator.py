from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

pdf.set_font("Arial", 'B', 18)
pdf.cell(0, 10, "Django ORM .filter() Cheat Sheet", ln=True, align="C")
pdf.ln(10)

def add_section(title):
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, title, ln=True)
    pdf.ln(3)

def add_content(text):
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, text)
    pdf.ln(3)

# Sections
add_section("1. Basic Syntax")
add_content("Model.objects.filter(<field lookups>)\nReturns a QuerySet (list-like object) containing all matching rows.")

add_section("2. Basic Filters")
add_content("""
Exact match: filter(name="Tech Daily")
Case-insensitive exact: filter(name__iexact="tech daily")
Contains: filter(name__contains="Tech")
Case-insensitive contains: filter(name__icontains="tech")
Starts with: filter(name__startswith="T")
Ends with: filter(name__endswith="y")
In a list: filter(id__in=[1,2,3])
Exclude results: exclude(name__icontains="tech")
""")

add_section("3. Date & Time Filters")
add_content("""
filter(pub_date__year=2025)  → Entries from 2025
filter(pub_date__month=10)  → Entries from October
filter(pub_date__gt="2025-01-01")  → After Jan 1, 2025
filter(pub_date__range=["2025-01-01", "2025-12-31"]) → Between two dates
""")

add_section("4. Numeric Filters")
add_content("""
filter(rating__gt=4) → Greater than 4
filter(rating__gte=4) → Greater or equal to 4
filter(price__range=(100,500)) → Between 100 and 500
""")

add_section("5. Filtering Across Relationships")
add_content("""
Entry.objects.filter(blog__name="Tech Daily") → Entries in blog “Tech Daily”
Blog.objects.filter(entry__headline__icontains="Django") → Blogs having entries with “Django”
Entry.objects.filter(authors__name="Alice") → Entries written by Alice
""")

add_section("6. Combining Filters (AND/OR/NOT)")
add_content("""
AND (default): Entry.objects.filter(pub_date__year=2025, blog__name="Tech Daily")
OR (Q objects): Entry.objects.filter(Q(headline__icontains="AI") | Q(headline__icontains="Python"))
NOT (~Q): Entry.objects.filter(~Q(pub_date__year=2025))
""")

add_section("7. Query Enhancements")
add_content("""
.order_by('pub_date') → Sort ascending
.order_by('-pub_date') → Sort descending
[:5] → Limit results
.first(), .last() → Get first/last record
.exists(), .count() → Check or count results
.values(), .distinct() → Return dict-like or unique results
""")

add_section("8. Example Recap")
add_content("""
Entry.objects.filter(pub_date__year=2025) → All 2025 entries
Entry.objects.filter(blog__name="Tech Daily") → Entries in Tech Daily
Entry.objects.filter(headline__icontains="pasta") → Entries with “pasta”
Entry.objects.filter(Q(headline__icontains="AI") | Q(headline__icontains="Smoothies")) → AI or Smoothies
""")

pdf.output("Django_Filter_CheatSheet.pdf")
print("✅ PDF created successfully: Django_Filter_CheatSheet.pdf")
