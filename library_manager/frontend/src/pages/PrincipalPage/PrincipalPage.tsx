import React, { useState } from 'react';
import { motion } from 'framer-motion';


const Card = ({ children, className = '' }) => (
  <div className={`p-4 bg-white rounded-lg shadow-md ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children }) => (
  <div className="mb-2 font-bold text-lg">{children}</div>
);

const CardContent = ({ children }) => (
  <div className="flex flex-col gap-2">{children}</div>
);

const Button = ({ variant = 'default', children, className = '', ...props }) => {
  const baseStyles = 'px-4 py-2 rounded-md font-medium transition';
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    outline: 'border border-blue-600 text-blue-600 hover:bg-blue-50',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};


const books = [
  {
    id: 1,
    title: 'En Familia con Karlos Arguiñano',
    summary: 'Delicious recipes for home cooking by Karlos Arguiñano.',
    image: '/mnt/data/libroCocina.jpg',
    reserved: false,
  },
  {
    id: 2,
    title: 'The Hound of the Baskervilles',
    summary: 'A classic Sherlock Holmes mystery by Arthur Conan Doyle.',
    image: '/mnt/data/libroMisterio.jpg',
    reserved: false,
  },
  {
    id: 3,
    title: 'Diez Negritos',
    summary: 'A thrilling mystery novel by Agatha Christie.',
    image: '/mnt/data/libroCrimen.jpg',
    reserved: false,
  },
];


const BookDisplayPage = () => {
  const [bookList, setBookList] = useState(books);

  const handleReserve = (id) => {
    setBookList((prevBooks) =>
      prevBooks.map((book) =>
        book.id === id && !book.reserved ? { ...book, reserved: true } : book
      )
    );
  };

  const handleViewDetails = (book) => {
    alert(`${book.title}: ${book.summary}`);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
      {bookList.map((book) => (
        <motion.div
          key={book.id}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Card className="rounded-2xl shadow-lg overflow-hidden">
            <motion.img
              src={book.image}
              alt={book.title}
              width="150"
              className="mb-6 rounded-full shadow-lg border-4 border-yellow-700"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            />
            <CardHeader>
              <h2 className="text-xl font-bold">{book.title}</h2>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => handleViewDetails(book)}
                variant="outline"
              >
                View Details
              </Button>
              <Button
                onClick={() => handleReserve(book.id)}
                disabled={book.reserved}
                variant="default"
              >
                {book.reserved ? 'Reserved' : 'Reserve'}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
};

export default BookDisplayPage;
