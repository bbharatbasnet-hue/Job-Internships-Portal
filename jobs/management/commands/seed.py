from django.core.management.base import BaseCommand
from accounts.models import Company, User
from jobs.models import Category, Job

class Command(BaseCommand):
    help="Create safe local demo data."
    def handle(self,*args,**opts):
        emp,_=User.objects.get_or_create(username="demo-employer",defaults={"role":"employer","first_name":"Aarav","last_name":"Sharma","email":"employer@example.test","company":"Northstar Labs"})
        emp.role="employer"; emp.company="Northstar Labs"; emp.set_password("demo12345"); emp.save()
        Company.objects.update_or_create(employer=emp,defaults={"name":"Northstar Labs","industry":"Technology","location":"Kathmandu, Nepal","size":"11-50","description":"Demo company profile for local client presentations.","featured":True})
        stu,_=User.objects.get_or_create(username="demo-seeker",defaults={"role":"student","first_name":"Sita","last_name":"Thapa","email":"seeker@example.test","location":"Nepalgunj, Nepal"})
        stu.role="student"; stu.set_password("demo12345"); stu.save()
        cats=[]
        for name,icon in [("Software & IT","fa-code"),("Design & Creative","fa-pen-nib"),("Data & Analytics","fa-chart-line"),("Marketing","fa-bullhorn"),("Finance","fa-coins"),("Human Resources","fa-users")]:
            cats.append(Category.objects.get_or_create(name=name,defaults={"icon":icon})[0])
        company=emp.company_profile
        rows=[("Python/Django Developer","job",cats[0],"Hybrid"),("UI/UX Design Intern","internship",cats[1],"Remote"),("Junior Data Analyst","job",cats[2],"On-site"),("Digital Marketing Intern","internship",cats[3],"Remote")]
        for title,kind,cat,work in rows:
            Job.objects.get_or_create(employer=emp,title=title,defaults={"company_profile":company,"company":company.name,"location":"Kathmandu, Nepal","job_type":kind,"workplace_type":"remote" if work=="Remote" else ("hybrid" if work=="Hybrid" else "onsite"),"category":cat,"description":"A sample opportunity created for demonstration. Replace this with the client's real vacancy information.","responsibilities":"Work with the team, contribute to deliverables, document your work, and communicate progress.","requirements":"Strong fundamentals, communication skills, and a willingness to learn.","qualifications":"Relevant academic background or equivalent practical experience.","skills":"Communication, Problem Solving, Teamwork","benefits":"Learning opportunities, mentorship, and a collaborative environment.","salary":"NPR 30,000 – 50,000" if kind=="job" else "Stipend available","salary_min":30000 if kind=="job" else 10000,"salary_max":50000 if kind=="job" else 20000,"status":"published","is_active":True,"featured":True})
        self.stdout.write(self.style.SUCCESS("Demo data ready. Login: demo-employer / demo12345 and demo-seeker / demo12345"))
