-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 21, 2024 at 05:23 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `sus`
--

-- --------------------------------------------------------

--
-- Table structure for table `proizvod`
--

CREATE TABLE `proizvod` (
  `id` int(11) NOT NULL,
  `naziv` varchar(100) NOT NULL,
  `kategorija` varchar(100) NOT NULL,
  `cena` int(11) NOT NULL,
  `slika` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `proizvod`
--

INSERT INTO `proizvod` (`id`, `naziv`, `kategorija`, `cena`, `slika`) VALUES
(2, 'Lenovo Punjac', 'Laptop Oprema', 3000, 'Lenovo Punjaclenovopunjac.jpg'),
(4, 'Asus ROG Strix G15 2022', 'Laptop', 109900, 'Asus ROG Strix G15 2022Asus ROG Strix G15 2024ROGSCAR.jpg'),
(6, 'Monitor LG', 'IT Oprema', 28000, '');

-- --------------------------------------------------------

--
-- Table structure for table `skladiste`
--

CREATE TABLE `skladiste` (
  `id` int(11) NOT NULL,
  `naziv` varchar(100) NOT NULL,
  `adresa` varchar(100) NOT NULL,
  `kapacitet` int(11) NOT NULL,
  `popunjeno` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `skladiste`
--

INSERT INTO `skladiste` (`id`, `naziv`, `adresa`, `kapacitet`, `popunjeno`) VALUES
(1, 'Gigatron Nis', 'Knjazevacka 10', 2000, 1550),
(3, 'Gigatron Kragujevac', 'Nikole Pasica 32', 5000, 1550);

-- --------------------------------------------------------

--
-- Table structure for table `skladisteproizvod`
--

CREATE TABLE `skladisteproizvod` (
  `id` int(11) NOT NULL,
  `skladiste_id` int(11) NOT NULL,
  `proizvod_id` int(11) NOT NULL,
  `kolicina` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `skladisteproizvod`
--

INSERT INTO `skladisteproizvod` (`id`, `skladiste_id`, `proizvod_id`, `kolicina`) VALUES
(2, 1, 2, 700),
(3, 1, 4, 250),
(4, 3, 2, 50),
(5, 3, 4, 1500),
(6, 1, 6, 600);

--
-- Triggers `skladisteproizvod`
--
DELIMITER $$
CREATE TRIGGER `update_popunjenost` AFTER INSERT ON `skladisteproizvod` FOR EACH ROW BEGIN DECLARE total_quantity INT; SET total_quantity = (SELECT SUM(kolicina) FROM skladisteproizvod WHERE skladiste_id = NEW.skladiste_id); UPDATE skladiste SET popunjeno = total_quantity WHERE id = NEW.skladiste_id; END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `update_popunjenost_after_delete` AFTER DELETE ON `skladisteproizvod` FOR EACH ROW BEGIN
    DECLARE total_quantity INT;
    SET total_quantity = (SELECT SUM(kolicina) FROM skladisteproizvod WHERE skladiste_id = OLD.skladiste_id);
    UPDATE skladiste SET popunjeno = total_quantity WHERE id = OLD.skladiste_id;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `update_popunjenost_after_update` AFTER UPDATE ON `skladisteproizvod` FOR EACH ROW BEGIN
    DECLARE total_quantity INT;
    SET total_quantity = (SELECT SUM(kolicina) FROM skladisteproizvod WHERE skladiste_id = NEW.skladiste_id);
    UPDATE skladiste SET popunjeno = total_quantity WHERE id = NEW.skladiste_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `ime` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `lozinka` varchar(500) NOT NULL,
  `role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `ime`, `prezime`, `email`, `lozinka`, `role`) VALUES
(1, 'Natalija', 'Simic', 'natalybulkica@gmail.com', 'scrypt:32768:8:1$16EeZEOVxdYl97M8$9bab6d320947ef31347ecbcd0bc9a478669b46f6d9b2eab909f76dc870b2f38f5fa621901d730e096cf48cecbc4b18e882d799d4334dad71f16ea07dfc9f3727', 'Administrator'),
(2, 'Nevena', 'Minic', 'nevenceminic@gmail.com', 'scrypt:32768:8:1$Dwg4357IX71hb5r5$48cfaf81175a2fc04ba84fa2c745b1dc9c3f36024ed3e92dca1c0c04ee45a17b51325688ff13be7c57bbb9d62e321e090baaa9ed9d22b85d1414dd0439ffa6b6', 'Menadzer'),
(7, 'Zika', 'Zikic', 'zika@gmail.com', 'scrypt:32768:8:1$IWVruwDvry32jdMt$be726a6cc49cb2d8dabb1430357c9e26965a4e5e64294fd72d0c7cf939eb304a6ec153c8606e1e24d48b2807a8cdc425514fe2e8f67bd890931e68679ba78298', 'Zaposleni');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `proizvod`
--
ALTER TABLE `proizvod`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `skladiste`
--
ALTER TABLE `skladiste`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `skladisteproizvod`
--
ALTER TABLE `skladisteproizvod`
  ADD PRIMARY KEY (`id`),
  ADD KEY `proizvod` (`proizvod_id`),
  ADD KEY `skladiste` (`skladiste_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `proizvod`
--
ALTER TABLE `proizvod`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `skladiste`
--
ALTER TABLE `skladiste`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `skladisteproizvod`
--
ALTER TABLE `skladisteproizvod`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `skladisteproizvod`
--
ALTER TABLE `skladisteproizvod`
  ADD CONSTRAINT `proizvod` FOREIGN KEY (`proizvod_id`) REFERENCES `proizvod` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `skladiste` FOREIGN KEY (`skladiste_id`) REFERENCES `skladiste` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
