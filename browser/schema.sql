-- --------------------------------------------------------
-- Table structure for table `basic_types`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `basic_types` (
    `basic_type` varchar(10) NOT NULL,
    `synset_number` int(11) NOT NULL,
    `synset_elements` varchar(255) NOT NULL,
    KEY `basic_type` (`basic_type`)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- --------------------------------------------------------
-- Table structure for table `corelex_types`
-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `corelex_types` (
    `corelex_type` varchar(5) NOT NULL,
    `polysemous_type` varchar(25) NOT NULL,
    KEY `basic_types` (`polysemous_type`),
    KEY `corelex_type` (`corelex_type`)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- --------------------------------------------------------
-- Table structure for table `nouns`
-- --------------------------------------------------------

CREATE TABLE `nouns` (
    `noun` varchar(255) COLLATE utf8mb4_bin NOT NULL,
    `corelex_type` varchar(5) COLLATE utf8mb4_bin NOT NULL,
    `polysemous_type` varchar(25) COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

ALTER TABLE `nouns`
    ADD PRIMARY KEY (`noun`(191)),
    ADD KEY `corelex_type` (`corelex_type`),
    ADD KEY `polysemous_type` (`polysemous_type`);
