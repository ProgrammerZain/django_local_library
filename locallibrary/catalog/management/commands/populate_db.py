from django.core.management.base import BaseCommand
from catalog.models import Genre, Language, Author, Book, BookInstance
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Populates the library catalog database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # 1. Create Languages
        languages_data = ['English', 'French', 'Spanish', 'German', 'Japanese']
        languages = {}
        for lang_name in languages_data:
            lang, created = Language.objects.get_or_create(name=lang_name)
            languages[lang_name] = lang
            if created:
                self.stdout.write(f'Created Language: {lang_name}')

        # 2. Create Genres
        genres_data = ['Fantasy', 'Science Fiction', 'Mystery', 'Historical Fiction', 'Non-Fiction', 'Romance']
        genres = {}
        for genre_name in genres_data:
            g, created = Genre.objects.get_or_create(name=genre_name)
            genres[genre_name] = g
            if created:
                self.stdout.write(f'Created Genre: {genre_name}')

        # 3. Create Authors
        authors_data = [
            {'first_name': 'J.K.', 'last_name': 'Rowling', 'dob': date(1965, 7, 31), 'dod': None},
            {'first_name': 'George R.R.', 'last_name': 'Martin', 'dob': date(1948, 9, 20), 'dod': None},
            {'first_name': 'Isaac', 'last_name': 'Asimov', 'dob': date(1920, 1, 2), 'dod': date(1992, 4, 6)},
            {'first_name': 'Agatha', 'last_name': 'Christie', 'dob': date(1890, 9, 15), 'dod': date(1976, 1, 12)},
            {'first_name': 'Arthur Conan', 'last_name': 'Doyle', 'dob': date(1859, 5, 22), 'dod': date(1930, 7, 7)},
        ]
        authors = {}
        for auth_info in authors_data:
            author, created = Author.objects.get_or_create(
                first_name=auth_info['first_name'],
                last_name=auth_info['last_name'],
                defaults={
                    'date_of_birth': auth_info['dob'],
                    'date_of_death': auth_info['dod']
                }
            )
            authors[f"{auth_info['first_name']} {auth_info['last_name']}"] = author
            if created:
                self.stdout.write(f'Created Author: {author}')

        # 4. Create Books (Multiple books per author & genre)
        books_data = [
            {
                'title': "Harry Potter and the Philosopher's Stone",
                'author': authors['J.K. Rowling'],
                'summary': "A young wizard discovers his magical heritage on his eleventh birthday when he receives an acceptance letter to Hogwarts School of Witchcraft and Wizardry.",
                'isbn': '9780747532699',
                'genres': [genres['Fantasy']],
                'language': languages['English']
            },
            {
                'title': "Harry Potter and the Chamber of Secrets",
                'author': authors['J.K. Rowling'],
                'summary': "Harry's second year at Hogwarts is marred by a series of mysterious attacks on students and dark secrets hidden within the Chamber of Secrets.",
                'isbn': '9780747538493',
                'genres': [genres['Fantasy']],
                'language': languages['English']
            },
            {
                'title': "A Game of Thrones",
                'author': authors['George R.R. Martin'],
                'summary': "Summers span decades. Winters can last a lifetime. And the struggle for the Iron Throne begins in the Seven Kingdoms of Westeros.",
                'isbn': '9780553103540',
                'genres': [genres['Fantasy']],
                'language': languages['English']
            },
            {
                'title': "A Clash of Kings",
                'author': authors['George R.R. Martin'],
                'summary': "A civil war tears apart Westeros as five rival kings claim the Iron Throne while a mysterious comet shines across the sky.",
                'isbn': '9780553108033',
                'genres': [genres['Fantasy']],
                'language': languages['English']
            },
            {
                'title': "Foundation",
                'author': authors['Isaac Asimov'],
                'summary': "Psychohistorian Hari Seldon foresees the collapse of the Galactic Empire and establishes a foundation to preserve human knowledge.",
                'isbn': '9780553293357',
                'genres': [genres['Science Fiction']],
                'language': languages['English']
            },
            {
                'title': "I, Robot",
                'author': authors['Isaac Asimov'],
                'summary': "A collection of nine science fiction short stories about the interactions between humans, robots, and morality guided by the Three Laws of Robotics.",
                'isbn': '9780553294385',
                'genres': [genres['Science Fiction']],
                'language': languages['English']
            },
            {
                'title': "Murder on the Orient Express",
                'author': authors['Agatha Christie'],
                'summary': "Belgian detective Hercule Poirot investigates the murder of an American tycoon aboard the famous Orient Express train.",
                'isbn': '9780007119319',
                'genres': [genres['Mystery']],
                'language': languages['English']
            },
            {
                'title': "And Then There Were None",
                'author': authors['Agatha Christie'],
                'summary': "Ten strangers are invited to an isolated island, only to be killed off one by one according to a sinister nursery rhyme.",
                'isbn': '9780007282630',
                'genres': [genres['Mystery']],
                'language': languages['English']
            },
            {
                'title': "A Study in Scarlet",
                'author': authors['Arthur Conan Doyle'],
                'summary': "The iconic story introducing consulting detective Sherlock Holmes and Dr. John Watson as they solve a complex murder case in London.",
                'isbn': '9780140439083',
                'genres': [genres['Mystery'], genres['Historical Fiction']],
                'language': languages['English']
            },
            {
                'title': "The Hound of the Baskervilles",
                'author': authors['Arthur Conan Doyle'],
                'summary': "Sherlock Holmes and Dr. Watson investigate the legend of a supernatural demonic hound haunting the Baskerville family on Dartmoor.",
                'isbn': '9780140437867',
                'genres': [genres['Mystery'], genres['Fantasy']],
                'language': languages['English']
            }
        ]

        created_books = []
        for b_info in books_data:
            book, created = Book.objects.get_or_create(
                isbn=b_info['isbn'],
                defaults={
                    'title': b_info['title'],
                    'author': b_info['author'],
                    'summary': b_info['summary'],
                    'language': b_info['language']
                }
            )
            if created:
                book.genre.set(b_info['genres'])
                self.stdout.write(f'Created Book: {book.title}')
            created_books.append(book)

        # 5. Create BookInstances (copies of books)
        imprints = ['Bloomsbury Publishing', 'HarperCollins', 'Bantam Books', 'Penguin Classics', 'Vintage Crime']
        statuses = ['a', 'o', 'd', 'r'] # available, on loan, maintenance, reserved

        for book in created_books:
            # Create 2-3 copies for each book
            for i in range(random.randint(2, 3)):
                st = random.choice(statuses)
                due = date.today() + timedelta(days=random.randint(5, 30)) if st in ['o', 'r'] else None
                inst = BookInstance.objects.create(
                    book=book,
                    imprint=random.choice(imprints),
                    due_back=due,
                    status=st
                )
                self.stdout.write(f'Created BookInstance for "{book.title}" (Status: {inst.get_status_display()})')

        self.stdout.write(self.style.SUCCESS('Database population complete!'))
