"""
PubChem API 集成模块
免费化学数据库查询接口
文档: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
"""

import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CompoundInfo:
    """化合物信息数据类"""
    cid: int
    name: str
    molecular_formula: str
    molecular_weight: float
    smiles: str
    iupac_name: str
    description: str
    synonyms: List[str]
    xlogp: Optional[float] = None
    h_bond_donor_count: Optional[int] = None
    h_bond_acceptor_count: Optional[int] = None
    rotatable_bond_count: Optional[int] = None
    exact_mass: Optional[float] = None
    monoisotopic_mass: Optional[float] = None
    tpsa: Optional[float] = None
    complexity: Optional[float] = None
    charge: Optional[int] = None


class PubChemAPI:
    """PubChem PUG REST API 客户端"""

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    RATE_LIMIT = 0.2  # 5 requests per second

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChemMaster/1.0 (Chemistry Editor)'
        })
        self._last_request_time = 0

    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT:
            time.sleep(self.RATE_LIMIT - elapsed)
        self._last_request_time = time.time()

    def _get(self, endpoint: str, format: str = "JSON") -> Any:
        """发送 GET 请求"""
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}/{format}"
        response = self.session.get(url, timeout=10)

        if response.status_code == 200:
            if format == "JSON":
                return response.json()
            return response.text
        elif response.status_code == 404:
            return None
        else:
            response.raise_for_status()

    def search_by_name(self, name: str) -> Optional[CompoundInfo]:
        """
        通过名称搜索化合物

        Args:
            name: 化合物名称（英文）

        Returns:
            化合物信息或 None
        """
        try:
            # 获取化合物属性
            data = self._get(f"compound/name/{name}/property/"
                           "MolecularFormula,MolecularWeight,SMILES,"
                           "IUPACName,XLogP,HBondDonorCount,"
                           "HBondAcceptorsCount,RotatableBondCount,"
                           "ExactMass,MonoisotopicMass,TPSA,Complexity,Charge")

            if not data or 'PropertyTable' not in data:
                return None

            props = data['PropertyTable']['Properties'][0]

            # 获取描述
            description = self._get_description(props.get('CID', 0))

            # 获取同义词
            synonyms = self._get_synonyms(props.get('CID', 0))

            return CompoundInfo(
                cid=props.get('CID', 0),
                name=name,
                molecular_formula=props.get('MolecularFormula', ''),
                molecular_weight=props.get('MolecularWeight', 0),
                smiles=props.get('CanonicalSMILES', ''),
                iupac_name=props.get('IUPACName', ''),
                description=description,
                synonyms=synonyms,
                xlogp=props.get('XLogP'),
                h_bond_donor_count=props.get('HBondDonorCount'),
                h_bond_acceptor_count=props.get('HBondAcceptorsCount'),
                rotatable_bond_count=props.get('RotatableBondCount'),
                exact_mass=props.get('ExactMass'),
                monoisotopic_mass=props.get('MonoisotopicMass'),
                tpsa=props.get('TPSA'),
                complexity=props.get('Complexity'),
                charge=props.get('Charge')
            )
        except Exception as e:
            print(f"Error searching by name: {e}")
            return None

    def search_by_smiles(self, smiles: str) -> Optional[CompoundInfo]:
        """
        通过 SMILES 搜索化合物

        Args:
            smiles: SMILES 表示式

        Returns:
            化合物信息或 None
        """
        try:
            data = self._get(f"compound/smiles/{smiles}/property/"
                           "MolecularFormula,MolecularWeight,SMILES,"
                           "IUPACName,XLogP,HBondDonorCount,"
                           "HBondAcceptorsCount,RotatableBondCount,"
                           "ExactMass,MonoisotopicMass,TPSA,Complexity,Charge")

            if not data or 'PropertyTable' not in data:
                return None

            props = data['PropertyTable']['Properties'][0]
            description = self._get_description(props.get('CID', 0))
            synonyms = self._get_synonyms(props.get('CID', 0))

            return CompoundInfo(
                cid=props.get('CID', 0),
                name=props.get('IUPACName', ''),
                molecular_formula=props.get('MolecularFormula', ''),
                molecular_weight=props.get('MolecularWeight', 0),
                smiles=props.get('CanonicalSMILES', ''),
                iupac_name=props.get('IUPACName', ''),
                description=description,
                synonyms=synonyms,
                xlogp=props.get('XLogP'),
                h_bond_donor_count=props.get('HBondDonorCount'),
                h_bond_acceptor_count=props.get('HBondAcceptorsCount'),
                rotatable_bond_count=props.get('RotatableBondCount'),
                exact_mass=props.get('ExactMass'),
                monoisotopic_mass=props.get('MonoisotopicMass'),
                tpsa=props.get('TPSA'),
                complexity=props.get('Complexity'),
                charge=props.get('Charge')
            )
        except Exception as e:
            print(f"Error searching by SMILES: {e}")
            return None

    def search_by_cid(self, cid: int) -> Optional[CompoundInfo]:
        """
        通过 CID 搜索化合物

        Args:
            cid: PubChem Compound ID

        Returns:
            化合物信息或 None
        """
        try:
            data = self._get(f"compound/cid/{cid}/property/"
                           "MolecularFormula,MolecularWeight,SMILES,"
                           "IUPACName,XLogP,HBondDonorCount,"
                           "HBondAcceptorsCount,RotatableBondCount,"
                           "ExactMass,MonoisotopicMass,TPSA,Complexity,Charge")

            if not data or 'PropertyTable' not in data:
                return None

            props = data['PropertyTable']['Properties'][0]
            description = self._get_description(cid)
            synonyms = self._get_synonyms(cid)

            return CompoundInfo(
                cid=cid,
                name=props.get('IUPACName', ''),
                molecular_formula=props.get('MolecularFormula', ''),
                molecular_weight=props.get('MolecularWeight', 0),
                smiles=props.get('CanonicalSMILES', ''),
                iupac_name=props.get('IUPACName', ''),
                description=description,
                synonyms=synonyms,
                xlogp=props.get('XLogP'),
                h_bond_donor_count=props.get('HBondDonorCount'),
                h_bond_acceptor_count=props.get('HBondAcceptorsCount'),
                rotatable_bond_count=props.get('RotatableBondCount'),
                exact_mass=props.get('ExactMass'),
                monoisotopic_mass=props.get('MonoisotopicMass'),
                tpsa=props.get('TPSA'),
                complexity=props.get('Complexity'),
                charge=props.get('Charge')
            )
        except Exception as e:
            print(f"Error searching by CID: {e}")
            return None

    def _get_description(self, cid: int) -> str:
        """获取化合物描述"""
        try:
            data = self._get(f"compound/cid/{cid}/description")
            if data and 'InformationList' in data:
                infos = data['InformationList']['Information']
                for info in infos:
                    if 'Description' in info:
                        return info['Description']
            return ""
        except:
            return ""

    def _get_synonyms(self, cid: int) -> List[str]:
        """获取化合物同义词"""
        try:
            data = self._get(f"compound/cid/{cid}/synonyms")
            if data and 'InformationList' in data:
                infos = data['InformationList']['Information']
                for info in infos:
                    if 'Synonym' in info:
                        return info['Synonym'][:10]  # 只返回前10个
            return []
        except:
            return []

    def get_3d_structure(self, cid: int) -> Optional[str]:
        """
        获取化合物 3D 结构（SDF 格式）

        Args:
            cid: PubChem Compound ID

        Returns:
            SDF 格式的 3D 结构或 None
        """
        try:
            self._rate_limit()
            url = f"{self.BASE_URL}/compound/cid/{cid}/record/SDF?record_type=3d"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            print(f"Error getting 3D structure: {e}")
            return None

    def get_2d_structure(self, cid: int) -> Optional[bytes]:
        """
        获取化合物 2D 结构（PNG 图片）

        Args:
            cid: PubChem Compound ID

        Returns:
            PNG 图片数据或 None
        """
        try:
            self._rate_limit()
            url = f"{self.BASE_URL}/compound/cid/{cid}/PNG?image_size=300x300"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Error getting 2D structure: {e}")
            return None

    def similarity_search(self, smiles: str, threshold: int = 90) -> List[Dict]:
        """
        相似性搜索

        Args:
            smiles: SMILES 表示式
            threshold: 相似度阈值 (0-100)

        Returns:
            相似化合物列表
        """
        try:
            self._rate_limit()
            url = f"{self.BASE_URL}/compound/fastsimilarity_2d/smiles/{smiles}/cids/JSON?Threshold={threshold}&MaxRecords=10"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'IdentifierList' in data:
                    return data['IdentifierList']['CID']
            return []
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []

    def substructure_search(self, smiles: str) -> List[Dict]:
        """
        子结构搜索

        Args:
            smiles: SMILES 表示式

        Returns:
            包含该子结构的化合物列表
        """
        try:
            self._rate_limit()
            url = f"{self.BASE_URL}/compound/substructure/smiles/{smiles}/cids/JSON"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'IdentifierList' in data:
                    return data['IdentifierList']['CID']
            return []
        except Exception as e:
            print(f"Error in substructure search: {e}")
            return []

    def formula_search(self, formula: str) -> List[int]:
        """
        分子式搜索

        Args:
            formula: 分子式

        Returns:
            匹配的 CID 列表
        """
        try:
            self._rate_limit()
            url = f"{self.BASE_URL}/compound/formula/{formula}/cids/JSON"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'IdentifierList' in data:
                    return data['IdentifierList']['CID']
            return []
        except Exception as e:
            print(f"Error in formula search: {e}")
            return []


# 全局实例
pubchem_api = PubChemAPI()


# 便捷函数
def search_compound(name: str) -> Optional[CompoundInfo]:
    """搜索化合物"""
    return pubchem_api.search_by_name(name)


def get_compound_info(cid: int) -> Optional[CompoundInfo]:
    """获取化合物信息"""
    return pubchem_api.search_by_cid(cid)


def search_by_smiles(smiles: str) -> Optional[CompoundInfo]:
    """通过 SMILES 搜索"""
    return pubchem_api.search_by_smiles(smiles)
