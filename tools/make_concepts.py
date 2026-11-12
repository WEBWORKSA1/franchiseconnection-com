"""Generates data/concepts.json — brand-neutral franchise category profiles.

Ranges are typical total-initial-investment bands observed across published
Franchise Disclosure Documents (Item 7) for each category. Individual brands vary;
users are told to verify every figure in the brand's current FDD.
Edit the table below and run:  python3 tools/make_concepts.py
"""
import json, os, re

# name | industry | min | max | fee | royalty | roles | tags | summary | watch-out
ROWS = r"""
Quick-service burger restaurant|Food & beverage|1200000|2800000|$35k–$50k|4–6%|semi,exec|sba,multi|High-volume drive-thru model with proven menus and national purchasing power.|Real estate and build-out dominate cost; labor scheduling makes or breaks margin.
Pizza delivery & carryout|Food & beverage|250000|800000|$20k–$35k|5–6%|owner,semi|sba,multi|Small footprint, delivery-heavy sales and simple kitchen workflow.|Third-party delivery fees and driver staffing squeeze unit margins.
Fast-casual bowls & salads|Food & beverage|450000|1200000|$30k–$45k|5–6%|owner,semi|sba,multi|Health-forward menus with lunch-heavy traffic in suburban and office areas.|Lunch dependence; check daypart mix in Item 19 if disclosed.
Specialty coffee café|Food & beverage|300000|900000|$30k–$45k|5–7%|owner,semi|sba,multi|Repeat daily visits, drive-thru formats growing fastest.|Morning rush staffing and real-estate visibility are critical.
Coffee kiosk / drive-thru hut|Food & beverage|150000|500000|$25k–$40k|5–7%|owner|sba|Low square footage and fast service with high beverage margins.|Site approvals and traffic patterns drive almost all results.
Smoothie & juice bar|Food & beverage|200000|550000|$25k–$35k|5–6%|owner,semi|sba,multi|Health-led beverages with simple prep and strong add-on sales.|Seasonality and produce costs; mall or strip location matters.
Frozen dessert & ice cream|Food & beverage|250000|650000|$25k–$40k|4–6%|owner|sba|Treat-driven traffic with high gross margins on product.|Strong seasonality outside warm climates.
Cookie & bakery shop|Food & beverage|300000|750000|$30k–$45k|5–6%|owner,semi|sba,multi|Gifting, catering and delivery broaden sales beyond walk-ins.|Early-morning production labor and shelf-life waste.
Chicken wings & sandwiches|Food & beverage|450000|1500000|$30k–$50k|5–6%|semi,exec|sba,multi|Strong takeout and delivery demand with sports-season peaks.|Commodity chicken price swings hit food cost.
Sub & sandwich shop|Food & beverage|200000|600000|$15k–$35k|5–8%|owner,semi|sba,multi|Simple operations, catering add-ons and non-traditional sites.|Saturated in many markets; check territory protection closely.
Food truck / mobile kitchen|Food & beverage|120000|350000|$15k–$35k|4–6%|owner|mobile|Event, office-park and festival sales without a lease.|Weather, permits and vehicle downtime.
Boutique fitness studio|Health & fitness|300000|700000|$40k–$60k|6–8%|semi|recurring,multi,sba|Membership revenue with class-based scheduling and premium pricing.|Instructor retention and member churn after the first year.
Full-size 24-hour gym|Health & fitness|900000|3500000|$20k–$50k|Flat or 5–7%|exec,semi|recurring,multi,sba|Low monthly price, high member count, mostly unstaffed hours.|Large build-out and equipment leases; competitive markets.
Pilates & reformer studio|Health & fitness|350000|750000|$40k–$60k|6–8%|semi|recurring,multi,sba|One of the fastest-growing studio formats with high per-class pricing.|Trend risk; check unit closures in Item 20.
Stretch & recovery studio|Health & fitness|250000|550000|$40k–$50k|6–8%|semi|recurring,sba|Assisted stretching and recovery memberships for active and older clients.|Newer category; validate repeat-visit rates with owners.
Kids' sports & fitness programs|Health & fitness|40000|120000|$20k–$40k|6–8%|owner|home,mobile,recurring|Coaches run classes at schools, parks and daycares — no storefront.|Owner does sales and scheduling; growth needs coaches.
Indoor pickleball club|Health & fitness|1500000|4000000|$50k–$75k|6–7%|exec,semi|recurring,multi|Membership courts, leagues and events in large-format spaces.|Very large lease or purchase; newer models with limited history.
Med spa & aesthetics|Beauty & wellness|500000|1300000|$50k–$65k|6–8%|semi,exec|recurring,multi|Injectables, laser and skin services with membership pricing.|Medical director rules vary by state or province.
Massage & spa membership|Beauty & wellness|400000|950000|$40k–$50k|5–7%|semi|recurring,multi,sba|Monthly membership model with therapist-delivered services.|Therapist recruitment is the constant constraint.
IV hydration & wellness lounge|Beauty & wellness|200000|550000|$45k–$60k|6–8%|semi|recurring|Drip therapy and wellness add-ons in compact clinics.|Clinical oversight and regulatory scrutiny.
Hair salon / blow-dry bar|Beauty & wellness|250000|650000|$30k–$45k|5–7%|semi|multi,sba|Stylist-driven services with retail product upsell.|Stylist turnover; suite-rental competition.
Salon suites (rental)|Beauty & wellness|1000000|3000000|$40k–$55k|3–6%|semi,exec|recurring,lowstaff|Rent private suites to independent beauty pros — landlord-style income.|Lease size and occupancy ramp-up period.
Kids' haircuts|Beauty & wellness|200000|400000|$25k–$35k|5–6%|owner,semi|sba|Family-focused salon with entertainment for children.|Small ticket; volume and location are everything.
Waxing & brow studio|Beauty & wellness|350000|700000|$40k–$50k|6%|semi|recurring,multi,sba|Recurring personal-care visits with membership options.|Esthetician licensing and staffing.
Residential maid service|Cleaning & restoration|90000|200000|$40k–$60k|5–7%|owner,semi|recurring,home,sba|Recurring weekly and biweekly cleans create predictable revenue.|Hiring and retaining cleaners is the whole game.
Commercial janitorial|Cleaning & restoration|10000|80000|$8k–$45k|5–10%|owner|recurring,b2b,home|Contract cleaning of offices and facilities, often via a regional master.|Some models sell you accounts — read Item 11 and 19 carefully.
Carpet & upholstery cleaning|Cleaning & restoration|60000|180000|$20k–$40k|5–7%|owner|mobile,home|Van-based service with residential and commercial customers.|Equipment financing and seasonality.
Water, fire & mold restoration|Cleaning & restoration|150000|400000|$40k–$60k|6–10%|owner,semi|mobile,b2b,sba|Insurance-driven emergency work with high average tickets.|Long receivables cycles with insurance carriers.
Window cleaning & pressure washing|Cleaning & restoration|60000|160000|$25k–$50k|6–8%|owner|mobile,home,recurring|Low-overhead exterior services with recurring commercial routes.|Weather and seasonality in northern markets.
Junk removal & hauling|Cleaning & restoration|150000|400000|$40k–$50k|7–8%|owner,semi|mobile,sba|Truck-based service with strong demand from moves and renovations.|Disposal fees and truck maintenance.
Non-medical senior home care|Senior care & health|100000|220000|$45k–$55k|5–6%|owner,semi|recurring,home,sba|Caregivers support older adults at home; aging demographics drive demand.|Caregiver recruiting, overtime rules and payer mix.
Senior placement & advisory|Senior care & health|60000|120000|$40k–$50k|5–7%|owner|home|Help families choose care communities; paid by communities on move-in.|Referral-fee rules differ by state; relationship-driven.
Chiropractic clinic|Senior care & health|250000|500000|$30k–$40k|5–7%|semi|recurring,multi,sba|Cash-based membership chiropractic, no insurance billing.|Doctor recruitment and corporate practice laws.
Physical therapy / rehab clinic|Senior care & health|300000|650000|$40k–$50k|5–7%|semi,exec|sba|Outpatient care with referral and insurance revenue.|Insurance reimbursement rates and clinician supply.
Hearing & vision services|Senior care & health|150000|400000|$30k–$45k|5–7%|semi|sba|Testing and devices for an aging population.|Clinical licensing; big-box retail competition.
Drug testing & background screening|Business services|70000|160000|$40k–$50k|6–8%|owner|b2b,recurring|B2B testing for employers with repeat contracts.|Lab partnerships and regulatory updates.
Tutoring & learning center|Children & education|100000|300000|$30k–$45k|8–10%|owner,semi|recurring,sba|After-school academic support with monthly enrollment.|Seasonal enrollment; online tutoring competition.
Kids' coding & STEM center|Children & education|150000|400000|$35k–$50k|7–8%|owner,semi|recurring,sba|Coding, robotics and camps with subscription pricing.|Instructor quality; tech curriculum updates.
Early education / child care center|Children & education|1500000|5000000|$60k–$75k|6–7%|exec|recurring,multi|Licensed child care with long enrollment lifetimes.|Very large build-out, licensing and staffing ratios.
Mobile kids' enrichment|Children & education|35000|100000|$20k–$35k|6–8%|owner|home,mobile,recurring|Dance, art, science or sports classes delivered at partner sites.|Owner-led sales; income caps without hiring instructors.
Swim school|Children & education|1500000|3500000|$50k–$65k|6%|exec,semi|recurring,multi|Year-round lessons with high member retention.|Pool construction cost and lifeguard staffing.
Music & arts school|Children & education|250000|550000|$40k–$50k|7–8%|semi|recurring|Lessons, bands and camps with monthly tuition.|Teacher scheduling and room utilization.
Pet grooming (mobile)|Pets|100000|250000|$40k–$50k|6–7%|owner,semi|mobile,recurring|Van-based grooming at the customer's home with recurring appointments.|Groomer recruiting; van financing.
Dog daycare & boarding|Pets|600000|1700000|$40k–$50k|6–7%|semi,exec|recurring,sba|Daycare memberships plus overnight boarding and grooming.|Large facility, zoning and noise rules.
Pet waste removal|Pets|50000|110000|$30k–$40k|7–8%|owner|home,mobile,recurring|Recurring yard service with very low overhead.|Route density takes time to build.
Pet supply & wash store|Pets|250000|600000|$35k–$45k|4–5%|semi|sba|Natural food and self-wash stations in neighborhood retail.|Online pet retail competition.
Dog training|Pets|60000|150000|$40k–$50k|6–8%|owner|home,mobile|In-home and group training programs.|Trainer certification and lead generation.
Lawn care & landscaping|Home services|80000|200000|$30k–$45k|6–8%|owner,semi|mobile,recurring,home|Recurring seasonal service with upsells like aeration and lighting.|Short season in cold climates.
Residential painting|Home services|80000|200000|$35k–$50k|6–7%|owner,semi|home,sba|Crew-based painting run by a manager-owner; low equipment cost.|Crew labor availability and weather.
Handyman & home repair|Home services|80000|190000|$40k–$50k|6–7%|owner,semi|mobile,home,sba|Small jobs with high demand from busy and aging homeowners.|Technician recruiting and licensing rules.
Plumbing / HVAC / electrical|Home services|100000|300000|$40k–$60k|6–8%|owner,semi|mobile,recurring,sba|Essential trades with maintenance-plan recurring revenue.|Licensed-tech shortages; some markets need a licensed qualifier.
Pest control|Home services|80000|200000|$40k–$50k|7–8%|owner|mobile,recurring|Quarterly service plans give strong recurring revenue.|Chemical licensing and regulation.
Pool cleaning & repair|Home services|60000|150000|$40k–$50k|6–8%|owner|mobile,recurring,home|Weekly routes in warm climates.|Climate-limited markets.
Roofing & exteriors|Home services|100000|260000|$40k–$60k|6–7%|owner,semi|home,sba|High-ticket projects with insurance-claim work.|Storm-driven demand can be lumpy.
Closet & garage organization|Home services|100000|250000|$40k–$50k|6%|owner|home,sba|Custom storage design and install with high average tickets.|Showroom optional; installer staffing.
Bathroom & kitchen remodeling|Home services|100000|280000|$40k–$60k|5–7%|owner,semi|home,sba|Design-build projects with large tickets and financing options.|Project management and subcontractor quality.
Home inspection|Real estate & finance|40000|110000|$25k–$40k|6–8%|owner|home,mobile|Inspections for buyers, sellers and insurers.|Tied to housing-market volume.
Real estate brokerage|Real estate & finance|50000|300000|$20k–$35k|6–8% or per-agent|owner,exec|b2b|Recruit agents under a national brand and share commissions.|Agent splits and cyclical housing markets.
Tax preparation office|Real estate & finance|50000|150000|$25k–$35k|10–15%|owner|recurring|Seasonal tax work with year-round bookkeeping add-ons.|Heavy seasonality; DIY software competition.
Business coaching & consulting|Business services|60000|130000|$50k–$90k|Flat monthly|owner|home,b2b,recurring|Coach small-business owners on growth with monthly retainers.|You sell your own expertise; slow start without a network.
Staffing & recruiting|Business services|100000|250000|$40k–$60k|Varies by gross margin|owner,semi|b2b,recurring|Temporary and permanent placement for local employers.|Payroll funding and economic cycles.
Print, sign & marketing center|Business services|250000|450000|$40k–$50k|5–6%|owner|b2b,sba|B2B printing, signage and marketing services.|Equipment leases; shift to digital marketing.
Shipping, print & mailbox store|Retail|200000|450000|$30k–$35k|5–6%|owner,semi|sba,multi|Shipping, notary and print services with steady foot traffic.|Carrier rate changes affect margins.
Phone & electronics repair|Retail|100000|260000|$30k–$40k|6–7%|owner|sba|Repairs and refurbished devices in small retail units.|Manufacturer self-repair programs.
Mattress & sleep store|Retail|150000|350000|$30k–$40k|4–6%|owner|sba|Specialty retail with appointment-based selling.|Online mattress competition.
Convenience store|Retail|300000|1500000|$15k–$50k|4–6%|owner,semi|multi|Daily-needs retail with fuel or food-service add-ons.|Thin margins; long hours.
Vending & micro-markets|Retail|50000|160000|$20k–$50k|Varies|owner|home,b2b,lowstaff|Unattended retail in offices and facilities.|Location contracts and restocking routes.
Oil change & quick lube|Automotive|250000|1100000|$30k–$40k|5–6%|semi,exec|multi,sba|Fast, high-frequency service with membership plans.|Real estate cost and EV adoption over time.
Auto repair & tire service|Automotive|200000|700000|$30k–$50k|5–7%|semi|sba|Full-service repair with fleet and warranty work.|Technician shortage.
Mobile auto detailing|Automotive|50000|130000|$25k–$40k|6–8%|owner|mobile,home|Van-based detailing and ceramic coatings.|Weather and owner-labor dependence.
Express car wash|Automotive|2500000|6000000|$40k–$75k|4–6%|exec|recurring,lowstaff|Unlimited wash memberships with minimal staff.|Land, equipment and permitting costs are very high.
Escape room & experience venue|Entertainment & recreation|250000|650000|$40k–$50k|6–7%|semi|sba|Group bookings, corporate events and parties.|Content refresh costs; novelty wears off.
Family entertainment center|Entertainment & recreation|1000000|3000000|$50k–$75k|5–6%|exec|multi|Trampoline, climbing or arcade venues with party revenue.|Insurance, safety and large lease.
Travel agency (home-based)|Travel|3000|35000|$0–$15k|Commission split|owner|home,lowstaff|Sell cruises and tours from home with host-agency support.|Commission-only income ramps slowly.
Select-service hotel|Hospitality & lodging|9000000|22000000|$60k–$75k|5–6% + fees|exec|multi|Brand-affiliated lodging with reservation systems and loyalty programs.|Capital intensive; long development timelines.
""".strip()

ROLE = {"owner": "Owner-operator", "semi": "Semi-absentee", "exec": "Executive / investor"}

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

out = []
for line in ROWS.splitlines():
    p = [x.strip() for x in line.split("|")]
    name, ind, mn, mx, fee, roy, roles, tags, summ, watch = p
    out.append({
        "id": slug(name), "name": name, "industry": ind,
        "min": int(mn), "max": int(mx), "fee": fee, "royalty": roy,
        "roles": roles.split(","), "tags": [t for t in tags.split(",") if t],
        "summary": summ, "watch": watch,
    })

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "data", "concepts.json"), "w") as f:
    json.dump({"updated": "2026-11-12", "note": "Typical ranges across published FDDs. Brands vary. Verify every figure in the brand's current FDD.", "roles": ROLE, "items": out}, f, indent=1)
print(len(out), "concepts")
